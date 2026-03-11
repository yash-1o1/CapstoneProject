# Functional Specification

This document defines how the system behaves: the user interface, user flows, API surface, and data models. All items trace back to the [requirements specification](requirements.md).

---

## UI Wireframe

```
+----------------------------------------------------------+
|  Team Chat                               Online Users: 3  |
+----------------------------------------------------------+
|                              |                            |
|   Chat Messages              |   Online Users             |
|                              |                            |
|   [10:01] Alice: Hi team!   |   * Alice                  |
|   [10:02] Bob: Hey Alice!   |   * Bob                    |
|   [10:03] -- Charlie joined -|   * Charlie                |
|   [10:03] Charlie: Morning! |                            |
|                              |                            |
|                              |                            |
|                              |                            |
+----------------------------------------------------------+
|  [Type a message...                         ] [Send]      |
+----------------------------------------------------------+
```

**Components:**
- **Header** -- App title and online user count
- **Chat area** (left/main) -- Scrollable message list, auto-scrolls on new messages
- **User sidebar** (right) -- List of connected display names
- **Input area** (bottom) -- Text input and Send button
- **Name modal** (overlay) -- Shown on page load before chat is visible

---

## User Flows

### Join Flow

```mermaid
sequenceDiagram
    participant U as User Browser
    participant S as Server
    participant DB as SQLite

    U->>U: Page loads, name modal appears
    U->>U: User enters display name
    U->>S: WebSocket connect
    U->>S: emit "user:join" { name }
    S->>S: Validate name (1-30 chars, non-empty)
    S->>S: Add user to connectedUsers map
    S->>DB: SELECT last 50 messages
    DB-->>S: Message rows
    S-->>U: emit "chat:history" [messages]
    S-->>U: emit "users:list" [all usernames]
    S->>All Others: emit "user:joined" { name }
    S->>All: emit "users:list" [updated list]
```

### Send Message Flow

```mermaid
sequenceDiagram
    participant U as Sender
    participant S as Server
    participant DB as SQLite
    participant O as Other Users

    U->>S: emit "message:send" { text }
    S->>S: Validate text (1-500 chars, non-empty)
    S->>DB: INSERT message (username, text, timestamp)
    DB-->>S: Inserted row with id and timestamp
    S->>All: emit "message:new" { id, username, text, timestamp }
```

### Disconnect Flow

```mermaid
sequenceDiagram
    participant U as Disconnecting User
    participant S as Server
    participant O as Other Users

    U->>S: WebSocket disconnect (close tab / network loss)
    S->>S: Remove user from connectedUsers map
    S->>O: emit "user:left" { name }
    S->>O: emit "users:list" [updated list]
```

---

## API / Event Specification

### REST Endpoints

| Method | Path | Response | Description | Traces To |
|--------|------|----------|-------------|-----------|
| GET | `/` | HTML | Serves the frontend application | -- |
| GET | `/health` | `{ status: "ok", uptime: <seconds> }` | Health check endpoint | NFR-04 |

### Socket.io Events: Client -> Server

| Event | Payload | Description | Traces To |
|-------|---------|-------------|-----------|
| `user:join` | `{ name: string }` | User requests to join with a display name | FR-01 |
| `message:send` | `{ text: string }` | User sends a chat message | FR-03 |

### Socket.io Events: Server -> Client

| Event | Payload | Description | Traces To |
|-------|---------|-------------|-----------|
| `chat:history` | `Message[]` | Last 50 messages, sent to joining user only | FR-06 |
| `message:new` | `Message` | New message broadcast to all connected users | FR-04 |
| `users:list` | `string[]` | Updated list of all online display names | FR-02 |
| `user:joined` | `{ name: string }` | Join notification broadcast to all users | FR-08 |
| `user:left` | `{ name: string }` | Leave notification broadcast to all users | FR-08 |

---

## Data Models

### Messages Table (SQLite)

```sql
CREATE TABLE IF NOT EXISTS messages (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    NOT NULL,
    text      TEXT    NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Message Object (returned by API)

```json
{
    "id": 1,
    "username": "Alice",
    "text": "Hello team!",
    "timestamp": "2026-03-11T14:30:00.000Z"
}
```

### Connected Users (in-memory, not persisted)

```
connectedUsers: Map<socketId, { name: string, joinedAt: Date }>
```

This map is held in server memory. It is rebuilt on server restart (all users reconnect).

---

## Validation Rules

| Field | Rule | Error Behavior |
|-------|------|---------------|
| Display name | 1-30 characters after trimming, non-empty | Server ignores the `user:join` event; client shows error |
| Message text | 1-500 characters after trimming, non-empty | Server ignores the `message:send` event; client shows error |
| Duplicate display names | Allowed | Simplicity per assumption A-04; users are distinguishable by their messages |

---

## System Notifications

System-generated messages appear in the chat area but are visually distinct (e.g., italic, muted color, no username):

- **"Alice joined the chat"** -- when a user connects
- **"Bob left the chat"** -- when a user disconnects

These are not stored in the database; they are transient events.
