"""Unit tests for the database module (tests/test_db.py).

Each test follows the AAA pattern (Arrange-Act-Assert) and traces
to requirements defined in docs/tests.md.
"""

import pytest
from db import init_database, insert_message, get_recent_messages


# UT-01: Create messages table on setup
def test_create_messages_table(db):
    """The messages table should exist after init_database()."""
    cursor = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
    )
    assert cursor.fetchone() is not None


# UT-02: Insert a message
def test_insert_message(db):
    """insert_message should return a dict with id, username, text, timestamp."""
    msg = insert_message(db, "Alice", "Hello!")

    assert msg["id"] == 1
    assert msg["username"] == "Alice"
    assert msg["text"] == "Hello!"
    assert "timestamp" in msg

    row_count = db.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    assert row_count == 1


# UT-03: Retrieve last 50 messages in chronological order
def test_get_recent_messages_limit(db):
    """get_recent_messages should return only the last 50, oldest first."""
    for i in range(60):
        insert_message(db, "User", f"Message {i}")

    messages = get_recent_messages(db, limit=50)

    assert len(messages) == 50
    assert messages[0]["text"] == "Message 10"
    assert messages[-1]["text"] == "Message 59"
    # Verify chronological order (ascending IDs)
    ids = [m["id"] for m in messages]
    assert ids == sorted(ids)


# UT-04: Retrieve when fewer than 50 messages exist
def test_get_recent_messages_fewer_than_limit(db):
    """Should return all messages when fewer than limit exist."""
    for i in range(5):
        insert_message(db, "User", f"Message {i}")

    messages = get_recent_messages(db, limit=50)

    assert len(messages) == 5
    assert messages[0]["text"] == "Message 0"
    assert messages[-1]["text"] == "Message 4"


# UT-05: Reject empty username
def test_reject_empty_username(db):
    """insert_message should raise ValueError for empty username."""
    with pytest.raises(ValueError, match="Username cannot be empty"):
        insert_message(db, "", "Hello!")

    with pytest.raises(ValueError, match="Username cannot be empty"):
        insert_message(db, "   ", "Hello!")


# UT-06: Reject empty message text
def test_reject_empty_message_text(db):
    """insert_message should raise ValueError for empty text."""
    with pytest.raises(ValueError, match="Message text cannot be empty"):
        insert_message(db, "Alice", "")

    with pytest.raises(ValueError, match="Message text cannot be empty"):
        insert_message(db, "Alice", "   ")


# UT-07: Reject message text over 500 characters
def test_reject_oversized_message(db):
    """insert_message should raise ValueError for text > 500 chars."""
    with pytest.raises(ValueError, match="cannot exceed 500 characters"):
        insert_message(db, "Alice", "x" * 501)


# UT-08: Reject display name over 30 characters
def test_reject_oversized_username(db):
    """insert_message should raise ValueError for username > 30 chars."""
    with pytest.raises(ValueError, match="cannot exceed 30 characters"):
        insert_message(db, "x" * 31, "Hello!")
