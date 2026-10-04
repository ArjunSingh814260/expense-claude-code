import os
import tempfile

# Point the app at a throwaway DB before app.py runs init_db()/seed_db() at import.
os.environ["SPENDLY_DB_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")

import pytest

import database.db as db
from app import app as flask_app


@pytest.fixture
def app(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "test.db"))
    db.init_db()
    db.seed_db()
    flask_app.config.update(TESTING=True)
    yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()
