# Assumptions Document

## Project Context

This project was initiated from a deliberately vague requirement: **"Build a chat application for team communication."** The purpose of this document is to transform that ambiguous request into concrete, bounded assumptions that guide every subsequent engineering decision.

This is a capstone project demonstrating the full software engineering lifecycle. The focus is on engineering rigor and traceability, not production-readiness.

---

## User Assumptions

| ID | Assumption | Rationale |
|----|-----------|-----------|
| A-01 | Target users are small team members (2-20 concurrent users) | The requirement says "team communication," implying a small, known group rather than a public platform |
| A-02 | Users access the application via a modern web browser (Chrome, Firefox, or Edge, last 2 major versions) | Web-based access requires no installation and is the most accessible option for a team tool |
| A-03 | There is a single shared chat room (no private DMs or multiple channels) | Simplest interpretation of "team communication"; a single shared space is the MVP |
| A-04 | Users identify themselves by choosing a display name on entry (no password-based authentication) | For an internal team tool with a small user base, lightweight identification is sufficient |
| A-05 | Users are on the same network or can reach the server URL | This is an internal team tool, not a public-facing application |
| A-06 | Messages are text-only (no file uploads, images, or rich media) | Text messaging is the core of "chat"; media support adds significant complexity without addressing the primary need |
| A-07 | Messages cannot be edited or deleted after sending | Simplifies the data model and avoids complex state synchronization issues |
| A-08 | Messages are persisted so that users joining later can see chat history | "Communication" implies continuity; a chat with no history would lose context |

## Technical Assumptions

| ID | Assumption | Rationale |
|----|-----------|-----------|
| A-09 | The server runs as a single Node.js process (no clustering or load balancing) | A 2-20 user system does not require horizontal scaling |
| A-10 | SQLite is sufficient for the persistence layer | File-based, zero-configuration database is appropriate for the expected data volume and concurrency |
| A-11 | WebSocket connectivity is available between client and server | Real-time messaging requires persistent bidirectional connections; WebSockets are the standard approach |
| A-12 | The application runs locally for development and demonstration | No cloud deployment is required for the capstone evaluation |
| A-13 | HTTPS is not required for local development | Encrypted transport is a production concern; localhost communication is inherently trusted |

## Constraints

| ID | Constraint | Rationale |
|----|-----------|-----------|
| A-14 | The project must be completable by a single developer | This is an individual capstone project |
| A-15 | No third-party authentication providers (OAuth, SSO, etc.) | Adds external dependencies and complexity beyond the project scope |

## Out of Scope

The following features are explicitly **not** included in this project. Each exclusion is a deliberate scoping decision, not an oversight:

- **User registration and password authentication** -- Display name entry is sufficient (A-04)
- **Private/direct messages** -- Single shared room only (A-03)
- **Multiple chat rooms or channels** -- Single shared room only (A-03)
- **Typing indicators** -- Nice-to-have, not core to "communication"
- **Read receipts** -- Nice-to-have, not core to "communication"
- **File and image uploads** -- Text-only (A-06)
- **Message editing and deletion** -- Simplifies persistence (A-07)
- **Message threading** -- Adds UI and data model complexity beyond MVP
- **Admin panel or moderation tools** -- Small trusted team (A-01)
- **Rate limiting** -- Small trusted team (A-01)
- **End-to-end encryption** -- Internal tool, local network (A-05, A-13)
- **Search functionality** -- History is loaded on join; search is a future enhancement
- **Push notifications** -- Users are expected to have the app open when communicating
