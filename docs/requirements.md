# Requirements Specification

## Functional Requirements

Each requirement traces back to one or more assumptions from [assumptions.md](assumptions.md).

| ID | Requirement | Traces To |
|----|------------|-----------|
| FR-01 | User shall enter a display name to join the chat room | A-03, A-04 |
| FR-02 | User shall see a list of currently connected users | A-01 |
| FR-03 | User shall be able to send text messages to the shared chat room | A-03, A-06 |
| FR-04 | All connected users shall receive new messages in real-time without refreshing | A-03, A-11 |
| FR-05 | Messages shall be persisted to a database | A-08, A-10 |
| FR-06 | On joining, the user shall see the last 50 messages as chat history | A-08 |
| FR-07 | Each message shall display the sender's name and a timestamp | A-06 |
| FR-08 | The system shall display notifications when users join or leave the chat | A-01 |

## Non-Functional Requirements

| ID | Requirement | Traces To |
|----|------------|-----------|
| NFR-01 | Message delivery latency shall be under 500ms on a local network | A-01, A-11 |
| NFR-02 | The system shall support at least 20 concurrent WebSocket connections | A-01 |
| NFR-03 | The application shall work in Chrome, Firefox, and Edge (last 2 major versions) | A-02 |
| NFR-04 | The server shall start and be ready to accept connections in under 5 seconds | A-09, A-10 |
| NFR-05 | The SQLite database shall handle the expected message volume without exceeding 100MB | A-10 |

## User Stories

### US-01: Join the Chat Room

> **As a** team member,
> **I want to** join the chat room by entering my display name,
> **So that** other team members know who I am.

**Acceptance Criteria:**
- A name entry prompt is shown when the page loads
- The user cannot proceed without entering a non-empty name (1-30 characters)
- After entering a name, the user is connected to the chat room
- The user's name appears in the online users list for all connected users

**Traces to:** FR-01, FR-02

---

### US-02: Send and Receive Messages

> **As a** team member,
> **I want to** send and receive messages in real-time,
> **So that** I can communicate with my colleagues without refreshing the page.

**Acceptance Criteria:**
- The user can type a message and send it by pressing Enter or clicking Send
- The message appears in the chat area for all connected users within 500ms
- Each message shows the sender's name and a timestamp
- Empty messages cannot be sent

**Traces to:** FR-03, FR-04, FR-07, NFR-01

---

### US-03: View Chat History

> **As a** team member,
> **I want to** see recent message history when I join the chat,
> **So that** I have context for the ongoing conversation.

**Acceptance Criteria:**
- On joining, the last 50 messages are displayed in chronological order
- History messages show the same format as live messages (name, text, timestamp)
- If there are fewer than 50 messages, all available messages are shown

**Traces to:** FR-05, FR-06

---

### US-04: See Who Is Online

> **As a** team member,
> **I want to** see who is currently online,
> **So that** I know who I am communicating with.

**Acceptance Criteria:**
- A sidebar or panel shows the list of currently connected users
- The list updates in real-time when users join or leave
- A system notification appears in the chat when a user joins or leaves

**Traces to:** FR-02, FR-08

## Acceptance Criteria Matrix

| Requirement | Testable Criterion | Test Type |
|------------|-------------------|-----------|
| FR-01 | Name prompt appears; user joins after entering valid name | UI, Integration |
| FR-02 | Online user list updates when users connect/disconnect | Integration |
| FR-03 | Sent message is received by all connected clients | Integration |
| FR-04 | Message delivery occurs without page refresh via WebSocket | Integration |
| FR-05 | Messages exist in SQLite database after being sent | Unit, Integration |
| FR-06 | Joining user receives last 50 messages from database | Integration |
| FR-07 | Messages display sender name and timestamp | UI |
| FR-08 | Join/leave notifications broadcast to all users | Integration |
| NFR-01 | Message round-trip time < 500ms on localhost | Integration |
| NFR-02 | 20 simultaneous WebSocket connections maintained | Integration |
| NFR-03 | UI renders correctly in Chrome, Firefox, Edge | UI (manual) |
| NFR-04 | Server ready in < 5 seconds from startup | Integration |
| NFR-05 | Database size remains reasonable under normal use | Unit |
