# Agent Instructions

Before modifying the repository:

1. Read `regulations.md`.
2. Read `GOAL.md`.
3. Read `spec.md`.
4. Read `TASKS.md`.

If instructions conflict, use this order of authority:

1. `regulations.md`
2. `GOAL.md`
3. `spec.md`
4. `TASKS.md`

## Priorities

1. Competition compliance
2. End-to-end working prototype
3. Context-aware sensitivity detection
4. Semantic replacement
5. Accuracy improvement
6. Performance optimization

## Development Rules

- Keep the MVP offline and process recorded video files.
- Do not implement real-time screen sharing for the Stage I MVP.
- Do not add cloud APIs without approval.
- Never use real credentials in tests.
- Prefer the simplest implementation that satisfies `spec.md`.
- Add tests for new sensitive-information detectors.
- Do not change project scope without updating `spec.md`.
- Do not fabricate benchmark results.

## Before completing a task

Run:
- unit tests
- end-to-end demo
- lint/type checks if configured

Report:
- what changed
- what remains incomplete
- known limitations
