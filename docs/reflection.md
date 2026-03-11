# Reflection Document

## How I Interpreted the Vague Requirement

The original requirement -- "build a chat application for team communication" -- is deliberately ambiguous. It doesn't specify target users, scale, features, technology, or deployment. My first step was to resist the urge to start coding and instead write down every assumption I was making. This produced the [assumptions document](assumptions.md), which became the foundation for every subsequent decision.

The key insight was recognizing that "team communication" implies a small, trusted group -- not a public platform. This single interpretation eliminated entire categories of features (authentication, moderation, rate limiting) and allowed me to focus on the core experience: real-time message exchange with persistence.

## Assumptions That Were Correct

- **Single chat room is sufficient** -- For a small team demo, one shared room covers the requirement without the complexity of room management.
- **Display name entry is enough for auth** -- For a capstone demonstration, it keeps the focus on engineering process rather than third-party OAuth integration.
- **SQLite is sufficient** -- Zero configuration, built into Python, and perfectly adequate for 20 concurrent users.
- **Vanilla JS over React** -- The frontend is simple enough (one page, three sections) that a framework would have added build complexity without proportional benefit.

## Assumptions That Could Be Challenged

- **No message editing/deletion** -- In a real team tool, the ability to correct mistakes is important. This was a scope trade-off.
- **No multiple channels** -- Even small teams benefit from topic-based channels. This would be the first feature to add in a v2.
- **No typing indicators** -- Small quality-of-life feature that adds real-time feel. Left out for scope but relatively easy to add.

## How the Architecture Evolved

The initial plan was to use Node.js with Socket.io, which is the most common stack for real-time chat tutorials. I switched to Python (Flask + Flask-SocketIO) because:

1. Python has built-in SQLite support, eliminating native module compilation issues on Windows
2. The code is more readable for evaluation
3. Flask-SocketIO provides equivalent real-time capabilities

The frontend remained vanilla HTML/CSS/JS throughout. The decision to avoid React was validated when the entire frontend was implemented in three small files with no build step.

## Where AI Assisted Most

AI (Claude) was most helpful in:

1. **Structuring the documentation** -- Ensuring traceability IDs (A-XX, FR-XX, UT-XX) connected across documents
2. **Generating the test strategy** -- Writing AAA-format test cases before implementation forced clearer API design
3. **Scaffolding boilerplate** -- Package files, project structure, and configuration setup
4. **Identifying security concerns** -- XSS prevention (using `textContent` over `innerHTML`), SQL injection prevention (parameterized queries)

The engineering decisions (scope, trade-offs, technology choices) were driven by the project requirements and constraints.

## What I Would Improve

Given more time, I would add:

1. **Authentication** -- Integrate with Azure Entra ID for proper identity management
2. **Multiple channels** -- Allow teams to organize conversations by topic
3. **Message search** -- Full-text search across chat history
4. **CI/CD pipeline** -- GitHub Actions for automated testing and Azure deployment
5. **Typing indicators** -- Show when someone is composing a message
6. **Message editing/deletion** -- Allow users to correct mistakes
7. **File sharing** -- Support image and document uploads via Azure Blob Storage
8. **Monitoring** -- Application Insights for production observability

## Engineering Principles Demonstrated

- **Documentation-Driven Development** -- Every document was written before the code it describes, forcing clarity of thought
- **Test-Driven Development** -- Test cases defined in docs/tests.md before implementation; unit tests written and passing before integration code
- **Traceability** -- Every requirement traces to an assumption, every test traces to a requirement, every code module traces to the architecture
- **Separation of Concerns** -- Database module, server logic, and frontend are independent and independently testable
- **Security by Default** -- XSS prevention and SQL injection prevention built into the initial implementation, not added as an afterthought
- **YAGNI (You Aren't Gonna Need It)** -- Deliberately avoided over-engineering (no clustering, no Redis, no React) for the actual scale of the project
