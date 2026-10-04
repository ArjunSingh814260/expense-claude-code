# Spec: User Registration

## Overview
Make the stub `GET /register` route into a working sign-up flow so new visitors can create a Spendly account. The route accepts a POST from the existing form in `templates/register.html`, checks the input, hashes the password, and inserts a row into the `users` table. On success it flashes a success message and redirects to `/login`, where the message is shown. Every authenticated feature after this one (login, profile, expenses) relies on accounts created here.

## Depends on
- Step 1: Database setup (`users` table, `get_db()` in `database/db.py`)

## Routes
- `GET /register`: render the registration form (already exists, unchanged)
- `POST /register`: validate the form, create the user, flash success, redirect to `/login`. Public (no login required).

## Database changes
None. The `users` table already has every column needed:
`id`, `name`, `email` (UNIQUE), `password_hash`, `created_at` (defaults to now).

## Templates
- **Modify** `templates/register.html`: repopulate `name` and `email` with the submitted values when validation fails (never repopulate `password`). Add `minlength="8"` to the password input.
- **Modify** `templates/login.html`: render flashed messages (category `success`) above the form, inside `.auth-card`.

## Files to change
- `app.py`: set `app.secret_key`, make `register` accept `["GET", "POST"]`, add the POST handling, and import `request`, `redirect`, `url_for` and `flash`
- `templates/register.html`: keep form values when there is an error
- `templates/login.html`: show flashed messages
- `database/db.py`: let `DB_PATH` be overridden by the `SPENDLY_DB_PATH` env var so tests use a temporary DB
- `static/css/style.css`: add an `.auth-success` style that mirrors `.auth-error` but uses `--accent` / `--accent-light`

## Files to create
- `tests/test_register.py`: pytest tests for the registration flow
- `tests/conftest.py`: app/client fixtures that point `DB_PATH` at a temporary SQLite file

## New dependencies
None. Uses `flask` and `werkzeug`, which are already in `requirements.txt`.

## Rules for implementation
- No SQLAlchemy or other ORM. Use raw `sqlite3` through `get_db()`.
- Use parameterised queries only. Never build SQL with string formatting.
- Hash passwords with `generate_password_hash(password, method="pbkdf2:sha256")`. The venv has no scrypt, so the default method fails.
- Normalise input before checking it: `name.strip()`, `email.strip().lower()`. Do not strip the password.
- Validation rules, checked in this order, showing one error at a time:
  1. All fields filled in → `"All fields are required."`
  2. Email looks valid (contains `@` and a `.` after it) → `"Please enter a valid email address."`
  3. Password is at least 8 characters → `"Password must be at least 8 characters."`
  4. Email not already registered → `"An account with that email already exists."`
- Detect duplicate emails by catching `sqlite3.IntegrityError` on insert, which is race-safe. A pre-check `SELECT` is optional, but the `IntegrityError` handler is required.
- On a validation error, re-render `register.html` with `error=...`, the submitted `name`/`email`, and HTTP 400.
- On success: `flash("Account created! Please sign in.", "success")` then `redirect(url_for("login"))` (302).
- Always close the DB connection, including on error paths (`try/finally`).
- Read the secret key from the environment with a dev fallback: `os.environ.get("SECRET_KEY", "dev-secret-change-me")`.
- Do not log the user in automatically. Sessions come in Step 3.
- Use CSS variables for every colour. No hardcoded hex values in new CSS.
- Templates extend `base.html` and use `url_for()` for internal links.

## Definition of done
- [ ] `GET /register` still renders the form with status 200
- [ ] A valid POST inserts exactly one row in `users` with a lowercased email and a `pbkdf2:sha256$...` hash (no plain-text password stored)
- [ ] A valid POST returns 302 to `/login`, and following it shows "Account created! Please sign in."
- [ ] Missing fields, a bad email, a short password and a duplicate email each re-render the form with the right error and status 400, and insert no row
- [ ] The duplicate check is case-insensitive (`Demo@Spendly.com` is rejected because `demo@spendly.com` exists)
- [ ] After an error, name and email stay filled in and the password field is empty
- [ ] The new user can be found with `SELECT * FROM users WHERE email = ?` and `check_password_hash` passes for their password
- [ ] `pytest` passes
