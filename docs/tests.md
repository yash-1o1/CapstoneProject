# Test Strategy and Test Cases

Tests are designed **before implementation** following a TDD approach. Each test traces to a requirement from [requirements.md](requirements.md).

**Testing stack:** pytest + python-socketio[client]

---

## Test Framework Setup

```
# Install test dependencies
pip install pytest python-socketio[client] requests
```

- **pytest** -- Test runner and assertions
- **python-socketio** -- Socket.io client for WebSocket event testing
- **requests** -- HTTP endpoint testing
- Test database: separate `test_chat.db` file, created fresh for each test session

---

## Unit Tests (`tests/test_db.py`)

### UT-01: Create messages table on setup

| | |
|---|---|
| **Traces to** | FR-05 |
| **Arrange** | Fresh SQLite database (in-memory or temp file) |
| **Act** | Call `init_database()` |
| **Assert** | `messages` table exists with columns: id, username, text, timestamp |

### UT-02: Insert a message

| | |
|---|---|
| **Traces to** | FR-05 |
| **Arrange** | Initialized database |
| **Act** | Call `insert_message(db, "Alice", "Hello!")` |
| **Assert** | Returns a message dict with id, username="Alice", text="Hello!", and a timestamp. Row count is 1. |

### UT-03: Retrieve last 50 messages in chronological order

| | |
|---|---|
| **Traces to** | FR-06 |
| **Arrange** | Insert 60 messages with sequential content |
| **Act** | Call `get_recent_messages(db, limit=50)` |
| **Assert** | Returns exactly 50 messages. First message is the 11th inserted (oldest 10 excluded). Messages are in ascending timestamp order. |

### UT-04: Retrieve messages when fewer than 50 exist

| | |
|---|---|
| **Traces to** | FR-06 |
| **Arrange** | Insert 5 messages |
| **Act** | Call `get_recent_messages(db, limit=50)` |
| **Assert** | Returns exactly 5 messages in chronological order |

### UT-05: Reject empty username

| | |
|---|---|
| **Traces to** | FR-01 |
| **Arrange** | Initialized database |
| **Act** | Call `insert_message(db, "", "Hello!")` |
| **Assert** | Raises ValueError or returns None |

### UT-06: Reject empty message text

| | |
|---|---|
| **Traces to** | FR-03 |
| **Arrange** | Initialized database |
| **Act** | Call `insert_message(db, "Alice", "")` |
| **Assert** | Raises ValueError or returns None |

### UT-07: Reject message text over 500 characters

| | |
|---|---|
| **Traces to** | FR-03 |
| **Arrange** | Initialized database |
| **Act** | Call `insert_message(db, "Alice", "x" * 501)` |
| **Assert** | Raises ValueError or returns None |

### UT-08: Reject display name over 30 characters

| | |
|---|---|
| **Traces to** | FR-01 |
| **Arrange** | Initialized database |
| **Act** | Call `insert_message(db, "x" * 31, "Hello!")` |
| **Assert** | Raises ValueError or returns None |

---

## Integration Tests (`tests/test_server.py`)

### IT-01: User joins and receives chat history

| | |
|---|---|
| **Traces to** | FR-01, FR-06 |
| **Arrange** | Start server with test DB seeded with 5 messages |
| **Act** | Connect socket client, emit `user:join` with `{ name: "Alice" }` |
| **Assert** | Client receives `chat:history` event with 5 messages. Client receives `users:list` containing "Alice". |

### IT-02: Message broadcast to all connected clients

| | |
|---|---|
| **Traces to** | FR-03, FR-04 |
| **Arrange** | Two socket clients connected and joined |
| **Act** | Client 1 emits `message:send` with `{ text: "Hello!" }` |
| **Assert** | Both clients receive `message:new` event with username, text, and timestamp |

### IT-03: Join notification broadcast to existing users

| | |
|---|---|
| **Traces to** | FR-08 |
| **Arrange** | Client 1 connected and joined as "Alice" |
| **Act** | Client 2 connects and joins as "Bob" |
| **Assert** | Client 1 receives `user:joined` event with `{ name: "Bob" }`. Client 1 receives updated `users:list` containing both "Alice" and "Bob". |

### IT-04: Leave notification on disconnect

| | |
|---|---|
| **Traces to** | FR-08 |
| **Arrange** | Two clients connected and joined |
| **Act** | Client 2 disconnects |
| **Assert** | Client 1 receives `user:left` event with Client 2's name. Client 1 receives updated `users:list` without Client 2. |

### IT-05: Message persistence to database

| | |
|---|---|
| **Traces to** | FR-05 |
| **Arrange** | Client connected and joined |
| **Act** | Client emits `message:send` with `{ text: "Persisted!" }` |
| **Assert** | Query the test database directly; the message row exists with correct username and text. |

### IT-06: Health endpoint returns OK

| | |
|---|---|
| **Traces to** | NFR-04 |
| **Arrange** | Server running |
| **Act** | Send `GET /health` |
| **Assert** | Response status is 200. Body contains `{ "status": "ok" }` with an uptime value. |

### IT-07: Static files served correctly

| | |
|---|---|
| **Traces to** | -- |
| **Arrange** | Server running |
| **Act** | Send `GET /` |
| **Assert** | Response status is 200. Content-Type is `text/html`. |

### IT-08: Invalid message rejected

| | |
|---|---|
| **Traces to** | FR-03 |
| **Arrange** | Client connected and joined |
| **Act** | Client emits `message:send` with `{ text: "" }` |
| **Assert** | No `message:new` event is broadcast. Client receives `error` event. |

---

## UI Tests (Manual Test Scripts)

### UI-01: Name prompt on page load

| | |
|---|---|
| **Traces to** | FR-01 |
| **Steps** | 1. Open http://localhost:5000 in browser. 2. Observe the page. |
| **Expected** | A modal/overlay prompts for a display name. The chat area is not visible or is behind the modal. |

### UI-02: Send and display message

| | |
|---|---|
| **Traces to** | FR-03, FR-07 |
| **Steps** | 1. Join the chat as "Alice". 2. Type "Hello!" in the input field. 3. Press Enter or click Send. |
| **Expected** | The message appears in the chat area with format: `[timestamp] Alice: Hello!`. The input field is cleared. |

### UI-03: Real-time message receipt

| | |
|---|---|
| **Traces to** | FR-04 |
| **Steps** | 1. Open two browser tabs. 2. Join as "Alice" in tab 1 and "Bob" in tab 2. 3. Send a message from tab 1. |
| **Expected** | The message appears in tab 2 within 1 second without refreshing. |

### UI-04: Online user list updates

| | |
|---|---|
| **Traces to** | FR-02, FR-08 |
| **Steps** | 1. Join as "Alice" in tab 1. 2. Join as "Bob" in tab 2. 3. Close tab 2. |
| **Expected** | Tab 1 shows "Bob" appearing in the user list on step 2. Tab 1 shows "Bob" removed and a "Bob left" notification on step 3. |

### UI-05: Chat history on join

| | |
|---|---|
| **Traces to** | FR-06 |
| **Steps** | 1. Join as "Alice" and send several messages. 2. Open a new tab, join as "Bob". |
| **Expected** | Bob sees Alice's previous messages displayed in the chat area. |

---

## Traceability Matrix

| Test ID | Type | Requirement(s) | Description |
|---------|------|----------------|-------------|
| UT-01 | Unit | FR-05 | Database table creation |
| UT-02 | Unit | FR-05 | Message insertion |
| UT-03 | Unit | FR-06 | Retrieve last 50 messages |
| UT-04 | Unit | FR-06 | Retrieve when fewer than 50 |
| UT-05 | Unit | FR-01 | Reject empty username |
| UT-06 | Unit | FR-03 | Reject empty message text |
| UT-07 | Unit | FR-03 | Reject oversized message |
| UT-08 | Unit | FR-01 | Reject oversized username |
| IT-01 | Integration | FR-01, FR-06 | Join and receive history |
| IT-02 | Integration | FR-03, FR-04 | Broadcast message to all |
| IT-03 | Integration | FR-08 | Join notification |
| IT-04 | Integration | FR-08 | Leave notification |
| IT-05 | Integration | FR-05 | Message persisted to DB |
| IT-06 | Integration | NFR-04 | Health endpoint |
| IT-07 | Integration | -- | Static file serving |
| IT-08 | Integration | FR-03 | Invalid input rejection |
| UI-01 | UI | FR-01 | Name prompt appears |
| UI-02 | UI | FR-03, FR-07 | Send and display message |
| UI-03 | UI | FR-04 | Real-time message receipt |
| UI-04 | UI | FR-02, FR-08 | Online user list updates |
| UI-05 | UI | FR-06 | Chat history on join |
