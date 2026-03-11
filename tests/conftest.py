import sys
import os
import pytest

# Add backend to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from db import init_database


@pytest.fixture
def db():
    """Provide a fresh in-memory SQLite database for each test."""
    conn = init_database(":memory:")
    yield conn
    conn.close()
