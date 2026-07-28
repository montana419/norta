# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from main import app
import database

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    """
    Creates a temporary SQLite database for every test run
    to keep test data isolated from production data.
    """
    test_db_path = tmp_path / "test_atlas.db"
    
    # Patch database path if database.py uses a variable like DB_NAME
    monkeypatch.setattr(database, "DB_PATH", str(test_db_path), raising=False)
    
    # Re-initialize test database schema
    database.init_db()
    yield