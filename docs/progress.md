# SDD ledger — plan: docs/superpowers/plans/2026-11-19-sai.md

- User instructions reviewed twice in design before code; design builder check found no material unanswered question.
- Pre-flight: Task 2 consumes Store and engine from Task 1; Task 3 consumes Store and build_context from Task 2; signatures aligned.
- Ruling: execute inline under sleep-time preapproval, with independent design/final reviews — tasks share state APIs; no per-task agent cost.
- Ruling: durable evidence lives in docs/ rather than deleting the only ledger — owner's evidence-preservation instruction takes precedence over skill scratch cleanup.
- Ruling: exact event IDs deduplicate where supplied; hosts without a turn/event ID cannot offer universal exactly-once delivery. Document this boundary; immediate repeated care gives no extra XP.
- Baseline: new isolated repository with design/research only, no pre-existing code/tests. Working branch pilot/first-playable, base c86a71a.
- Task 1 RED: first suite exit 1, missing `sai.engine` and `sai.store` before implementation. First implemented run: 15 tests, 1 ERROR in fixture cleanup (Windows SQLite handle). Root cause: sqlite connection context commits but does not close; changed test fixture to contextlib.closing. Production store already closed in finally. FAIL retained here.
- Task 1 verification: `python -m unittest discover -s tests -v` exit 0, 15 tests PASS after fixture fix. A combined shell command containing recursive temp cleanup was rejected before execution (`blocked by policy`); no test/commit from that rejected call is counted.
- Task 1 complete: 202c99a. The known test DB and then its empty temp directory were removed with exact non-recursive paths; exit 0. No trust settings changed.
- Task 2 RED: command suite had 4 failures and one missing-context-module error, exit 1. CLI source not yet implemented. Fixed one test's unchecked setup so it cannot pass just because creation failed.
- Task 2 implemented-run FAIL: 27 tests, 1 failure. Hook off command included the disabled character in its result prefix. Removed that prefix when disabled so the next host context contains only the deactivation instruction.
- Task 2 complete: full suite 27 PASS, task-done exit 0; commit 0ccbf5b. The helper ran immediately before commit to honor verification-before-commit; its scratch ledger range was 202c99a..202c99a (uncommitted implementation), the actual implementation range is 202c99a..0ccbf5b. Demo command ran the real engine; dialogue is labelled scripted.
- Task 3 RED: missing chat/backends modules, exit 1. Implemented CLI subprocess adapter and bounded intent -> state -> dialogue pipeline. Full suite: 41 PASS, exit 0. Real-model verification uses only synthetic characters and separate temporary state.
