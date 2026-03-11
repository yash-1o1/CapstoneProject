"""Integration tests for the Flask-SocketIO server (tests/test_server.py).

Each test follows AAA pattern and traces to docs/tests.md.
"""

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import create_app
from db import insert_message


@pytest.fixture
def app_fixture():
    """Create a test app with an in-memory database."""
    app, socketio, db = create_app(db_path=":memory:")
    app.config["TESTING"] = True
    return app, socketio, db


@pytest.fixture
def client(app_fixture):
    """Provide a Flask test client."""
    app, socketio, db = app_fixture
    return app.test_client()


@pytest.fixture
def socket_client(app_fixture):
    """Provide a single SocketIO test client."""
    app, socketio, db = app_fixture
    return socketio.test_client(app)


# IT-06: Health endpoint returns OK
def test_health_endpoint(client):
    """GET /health should return status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "uptime" in data


# IT-07: Static files served correctly
def test_index_serves_html(client):
    """GET / should return 200 and HTML content."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"html" in response.data.lower()


# IT-01: User joins and receives chat history
def test_join_receives_history(app_fixture):
    """A joining user should receive chat:history with existing messages."""
    app, socketio, db = app_fixture

    # Arrange: seed DB with messages
    for i in range(5):
        insert_message(db, "Seeder", f"Seeded message {i}")

    # Act: connect and join
    client = socketio.test_client(app)
    client.emit("user:join", {"name": "Alice"})

    # Assert: check received events
    received = client.get_received()
    event_names = [r["name"] for r in received]

    assert "chat:history" in event_names
    history_event = next(r for r in received if r["name"] == "chat:history")
    messages = history_event["args"][0]
    assert len(messages) == 5
    assert messages[0]["text"] == "Seeded message 0"

    client.disconnect()


# IT-02: Message broadcast to all connected clients
def test_message_broadcast(app_fixture):
    """A message sent by one user should be received by all."""
    app, socketio, db = app_fixture

    # Arrange: two clients connected
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)
    client1.emit("user:join", {"name": "Alice"})
    client2.emit("user:join", {"name": "Bob"})

    # Clear received events from join
    client1.get_received()
    client2.get_received()

    # Act: client1 sends a message
    client1.emit("message:send", {"text": "Hello from Alice!"})

    # Assert: both receive message:new
    received1 = client1.get_received()
    received2 = client2.get_received()

    msg_events1 = [r for r in received1 if r["name"] == "message:new"]
    msg_events2 = [r for r in received2 if r["name"] == "message:new"]

    assert len(msg_events1) >= 1
    assert len(msg_events2) >= 1
    assert msg_events1[0]["args"][0]["text"] == "Hello from Alice!"
    assert msg_events2[0]["args"][0]["username"] == "Alice"

    client1.disconnect()
    client2.disconnect()


# IT-03: Join notification broadcast to existing users
def test_join_notification(app_fixture):
    """When a new user joins, existing users should receive user:joined."""
    app, socketio, db = app_fixture

    # Arrange: client1 already joined
    client1 = socketio.test_client(app)
    client1.emit("user:join", {"name": "Alice"})
    client1.get_received()  # clear

    # Act: client2 joins
    client2 = socketio.test_client(app)
    client2.emit("user:join", {"name": "Bob"})

    # Assert: client1 received user:joined
    received1 = client1.get_received()
    join_events = [r for r in received1 if r["name"] == "user:joined"]
    assert len(join_events) >= 1
    assert join_events[0]["args"][0]["name"] == "Bob"

    # Assert: client1 received updated users:list with both names
    list_events = [r for r in received1 if r["name"] == "users:list"]
    assert len(list_events) >= 1
    user_list = list_events[-1]["args"][0]
    assert "Alice" in user_list
    assert "Bob" in user_list

    client1.disconnect()
    client2.disconnect()


# IT-04: Leave notification on disconnect
def test_leave_notification(app_fixture):
    """When a user disconnects, others should receive user:left."""
    app, socketio, db = app_fixture

    # Arrange: two clients connected
    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)
    client1.emit("user:join", {"name": "Alice"})
    client2.emit("user:join", {"name": "Bob"})
    client1.get_received()  # clear

    # Act: client2 disconnects
    client2.disconnect()

    # Assert: client1 receives user:left
    received1 = client1.get_received()
    left_events = [r for r in received1 if r["name"] == "user:left"]
    assert len(left_events) >= 1
    assert left_events[0]["args"][0]["name"] == "Bob"

    # Assert: updated users:list without Bob
    list_events = [r for r in received1 if r["name"] == "users:list"]
    assert len(list_events) >= 1
    assert "Bob" not in list_events[-1]["args"][0]

    client1.disconnect()


# IT-05: Message persistence to database
def test_message_persistence(app_fixture):
    """Sent messages should be persisted in the database."""
    app, socketio, db = app_fixture

    # Arrange
    client = socketio.test_client(app)
    client.emit("user:join", {"name": "Alice"})
    client.get_received()  # clear

    # Act
    client.emit("message:send", {"text": "Persisted message!"})

    # Assert: query DB directly
    row = db.execute("SELECT * FROM messages WHERE text = ?", ("Persisted message!",)).fetchone()
    assert row is not None
    assert row["username"] == "Alice"

    client.disconnect()


# IT-08: Invalid message rejected
def test_invalid_message_rejected(app_fixture):
    """Empty messages should not be broadcast."""
    app, socketio, db = app_fixture

    client1 = socketio.test_client(app)
    client2 = socketio.test_client(app)
    client1.emit("user:join", {"name": "Alice"})
    client2.emit("user:join", {"name": "Bob"})
    client1.get_received()
    client2.get_received()

    # Act: send empty message
    client1.emit("message:send", {"text": ""})

    # Assert: client2 should NOT receive message:new
    received2 = client2.get_received()
    msg_events = [r for r in received2 if r["name"] == "message:new"]
    assert len(msg_events) == 0

    # Assert: client1 should receive an error
    received1 = client1.get_received()
    error_events = [r for r in received1 if r["name"] == "error"]
    assert len(error_events) >= 1

    client1.disconnect()
    client2.disconnect()
