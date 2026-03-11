# Team Chat Application

A real-time team chat application built as a capstone project demonstrating the full software engineering lifecycle.

## Features

- Join with a display name (no registration required)
- Send and receive messages in real-time via WebSockets
- Message persistence with SQLite
- Chat history loaded on join (last 50 messages)
- Online user list with join/leave notifications

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12 + Flask + Flask-SocketIO |
| Frontend | Vanilla HTML/CSS/JavaScript |
| Database | SQLite (built-in) |
| WebSocket | Socket.io |
| Testing | pytest |

## Prerequisites

- Python 3.10+ ([python.org](https://www.python.org/downloads/))

## Setup & Run

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Start the server
python app.py
```

Open your browser to **http://localhost:5000**

## Running Tests

```bash
# From the project root
python -m pytest tests/ -v
```

## Project Structure

```
CapstoneProject/
├── backend/
│   ├── app.py             # Flask + Socket.io server
│   ├── db.py              # SQLite database module
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── index.html         # Chat UI
│   ├── style.css          # Styling
│   └── app.js             # Client-side Socket.io logic
├── tests/
│   ├── conftest.py        # Test fixtures
│   ├── test_db.py         # Unit tests (8 tests)
│   └── test_server.py     # Integration tests (8 tests)
└── docs/
    ├── assumptions.md     # Scoping assumptions
    ├── requirements.md    # Functional & non-functional requirements
    ├── functional-spec.md # UI wireframes, API events, data models
    ├── architecture.md    # Tech stack, diagrams, security, risks
    ├── tests.md           # Test strategy (written before code)
    └── reflection.md      # Engineering process reflection
```

## Documentation

Each document traces to the previous, forming a chain:

**Assumptions** --> **Requirements** --> **Functional Spec** --> **Architecture** --> **Tests** --> **Code**

See the [docs/](docs/) folder for all artifacts.
