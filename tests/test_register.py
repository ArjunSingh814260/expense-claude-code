from werkzeug.security import check_password_hash

from database.db import get_db

VALID = {"name": "Asha Rao", "email": "Asha.Rao@Example.com", "password": "secret123"}


def user_count():
    conn = get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:
        conn.close()


def test_get_register_renders_form(client):
    resp = client.get("/register")
    assert resp.status_code == 200
    assert b"Create your account" in resp.data


def test_valid_registration_creates_user_and_redirects(client):
    resp = client.post("/register", data=VALID)
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/login")

    conn = get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", ("asha.rao@example.com",)).fetchone()
    conn.close()
    assert row["name"] == "Asha Rao"
    assert row["password_hash"].startswith("pbkdf2:sha256")
    assert check_password_hash(row["password_hash"], "secret123")


def test_success_message_shown_on_login(client):
    resp = client.post("/register", data=VALID, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Account created! Please sign in." in resp.data


def test_missing_field(client):
    resp = client.post("/register", data={**VALID, "name": "   "})
    assert resp.status_code == 400
    assert b"All fields are required." in resp.data


def test_invalid_email(client):
    resp = client.post("/register", data={**VALID, "email": "foo"})
    assert resp.status_code == 400
    assert b"Please enter a valid email address." in resp.data


def test_short_password(client):
    resp = client.post("/register", data={**VALID, "password": "short"})
    assert resp.status_code == 400
    assert b"Password must be at least 8 characters." in resp.data


def test_duplicate_email_case_insensitive(client):
    before = user_count()
    resp = client.post("/register", data={**VALID, "email": "Demo@Spendly.com"})
    assert resp.status_code == 400
    assert b"An account with that email already exists." in resp.data
    assert user_count() == before


def test_error_keeps_name_and_email_but_not_password(client):
    before = user_count()
    resp = client.post("/register", data={**VALID, "password": "short"})
    assert b'value="Asha Rao"' in resp.data
    assert b'value="asha.rao@example.com"' in resp.data
    assert b"short" not in resp.data
    assert user_count() == before
