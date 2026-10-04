# Spec: Login and Logout

## Overview
Make the stub `/login` route into a working sign-in flow and implement the `/logout` stub. On login, the app looks up the user by email, checks the password with `check_password_hash`, stores the user's ID in Flask's `session`, and redirects to the signed-in landing page. On logout, the app clears the session and returns to the landing page. A `login_required` decorator and a per-request `g.user` let the app tell logged-in users from guests, which every expense feature after this one needs.

## Depends on
- Step 1: Database setup (`users` table, `get_db()`)
- Step 2: Registration (`app.secret_key`, flash messages on `login.html`, pbkdf2 password hashes)

## Routes
- `GET /login`: render the sign-in form. If already logged in, redirect to `/profile`.
- `POST /login`: verify credentials, set `session["user_id"]`, redirect to `/profile`. Public.
- `GET /logout`: clear the session, flash "You have been signed out.", redirect to `/`. Works when logged out too (no error).
- `GET /register`: unchanged, except that a logged-in user is redirected to `/profile`.

**Redirect target:** there is no dashboard yet. `/profile` (Step 4) is the signed-in landing page, so login redirects there. While it is still a placeholder, it is protected by `login_required` and its text includes the user's name, which proves the session works.

## Database changes
None. Reads `users.id`, `users.name`, `users.email`, `users.password_hash`.

## Templates
- **Modify** `templates/base.html`: make the navbar depend on login state.
  - Guest: "Sign in" and "Get started" (as now)
  - Logged in: the user's name and a "Sign out" link to `url_for('logout')`
- **Modify** `templates/login.html`: repopulate `email` after a failed attempt (never `password`).
- **Modify** `templates/landing.html`: render flashed messages so "You have been signed out." is visible. Reuse the `.auth-success` style, or put a shared flash partial in `base.html` (preferred; then remove the per-page loop from `login.html`).

## Files to change
- `app.py`: `login` (GET/POST), `logout`, `login_required` decorator, a `before_request` hook that loads `g.user`, a redirect away from `/register` and `/login` when logged in, and `@login_required` on `/profile` and the expense placeholder routes
- `templates/base.html`: login-aware navbar and a shared flash-message block
- `templates/login.html`: keep the email after an error; drop its flash loop if `base.html` takes over
- `static/css/style.css`: only if the navbar username needs a style (use existing variables)

## Files to create
- `tests/test_auth.py`: login/logout/session tests (reuse the fixtures in `tests/conftest.py`)

## New dependencies
None. Uses `flask.session`, `flask.g`, `functools.wraps` and `werkzeug.security.check_password_hash`.

## Rules for implementation
- No ORM. Use raw `sqlite3` through `get_db()` with parameterised queries, and close connections in `finally`.
- Normalise the email with `.strip().lower()` before lookup, the same as registration.
- Verify with `check_password_hash(row["password_hash"], password)`. Never compare hashes or plain text directly.
- Use **one generic error** for an unknown email or a wrong password: `"Invalid email or password."` (no hints about which one). Use `"All fields are required."` for empty fields. Return HTTP 400 for errors.
- On success: call `session.clear()` first (to prevent session fixation), then `session["user_id"] = row["id"]`. Store only the ID, never the email, name or hash.
- `before_request`: if `session` has a `user_id`, load `id, name, email` into `g.user`, otherwise set `g.user = None`. If the ID no longer exists in the DB, clear the session and set `g.user = None`.
- `login_required`: if `g.user is None`, `flash("Please sign in to continue.", "error")` and redirect to `url_for("login")`. Use `functools.wraps`.
- `logout`: call `session.clear()`. Keep it GET so the navbar link works. CSRF protection is out of scope.
- Use `url_for()` for every redirect and link. Use CSS variables only; no hardcoded colours.
- No "remember me", no `next=` redirect parameter, no rate limiting (out of scope).

## Definition of done
- [ ] `GET /login` renders the form (200) for guests and redirects logged-in users to `/profile`
- [ ] Correct credentials (`demo@spendly.com` / `demo123`) return 302 to `/profile`, and `session["user_id"]` equals the demo user's ID
- [ ] The email check ignores case and spaces (`  DEMO@Spendly.com ` logs in)
- [ ] A wrong password and an unknown email both return 400 with exactly "Invalid email or password." and leave no `user_id` in the session
- [ ] Empty fields return 400 with "All fields are required."
- [ ] After a failed login the email stays filled in and the password field is empty
- [ ] `/profile` and the expense placeholders redirect guests to `/login` with "Please sign in to continue."
- [ ] `/profile` responds 200 for a logged-in user and shows their name
- [ ] The navbar shows "Sign out" and the user's name when logged in, and "Sign in"/"Get started" when not
- [ ] `/logout` clears the session, redirects to `/` and shows "You have been signed out."; after that `/profile` redirects to `/login`
- [ ] A user registered in Step 2 can log in with their new password
- [ ] All tests pass, including the existing `tests/test_register.py`
