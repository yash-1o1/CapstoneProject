import sqlite3
from datetime import datetime, timezone


def init_database(db_path=None):
    """Initialize the SQLite database and create the messages table."""
    if db_path is None:
        db_path = "chat.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT    NOT NULL,
            text      TEXT    NOT NULL,
            timestamp TEXT    NOT NULL
        )
    """)
    conn.commit()
    return conn


def validate_username(username):
    """Validate a display name: 1-30 non-empty characters after stripping."""
    if not username or not username.strip():
        raise ValueError("Username cannot be empty")
    username = username.strip()
    if len(username) > 30:
        raise ValueError("Username cannot exceed 30 characters")
    return username


def validate_message_text(text):
    """Validate message text: 1-500 non-empty characters after stripping."""
    if not text or not text.strip():
        raise ValueError("Message text cannot be empty")
    text = text.strip()
    if len(text) > 500:
        raise ValueError("Message text cannot exceed 500 characters")
    return text


def insert_message(conn, username, text):
    """Insert a message into the database and return the message dict."""
    username = validate_username(username)
    text = validate_message_text(text)
    timestamp = datetime.now(timezone.utc).isoformat()
    cursor = conn.execute(
        "INSERT INTO messages (username, text, timestamp) VALUES (?, ?, ?)",
        (username, text, timestamp),
    )
    conn.commit()
    return {
        "id": cursor.lastrowid,
        "username": username,
        "text": text,
        "timestamp": timestamp,
    }


def get_recent_messages(conn, limit=50):
    """Return the last `limit` messages in chronological order."""
    rows = conn.execute(
        "SELECT id, username, text, timestamp FROM messages ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(row) for row in reversed(rows)]
