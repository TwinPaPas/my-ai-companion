# Independent review and correction

The independent reviewer inspected `c86a71a..bc4f055` read-only and reproduced ten findings. It recommended withholding merge/publication. The implementation branch remained unpublished while these were corrected.

Initial regression run: **FAIL**, 12 tests, 9 failures and 3 errors (before fixes). This is an expected RED run, not a passing release check.

| Finding | Correction and evidence |
|---|---|
| Selection race could write A's input/history to B | Expected character checked inside write transaction; one read transaction supplies state/memories/history; final history insert checks original character. Race regressions pass. |
| Replayed remember/off/use/action could mutate again or affect a new character | Command event ID and mutation commit in the same transaction, independent of current character. Replay regressions pass. |
| PATH/cwd could change hook execution target | Fixed interpreter, isolated Python `-I`; Claude exec argv; Codex host-shell command. Installed wheel tested with a shadow `sai.py`, hostile PYTHONPATH and spaces in interpreter path. |
| Korean UTF-8 input was decoded through cp949 | Raw stdin bytes decoded explicitly as UTF-8. Legacy-encoding process regression and installed hook checks pass. |
| Incomplete schema version 1 could be modified | Validate required columns, types, nullability and primary keys before yielding the transaction. Foreign-table regression preserves original value. |
| Failed hook omitted mode deactivation | Error response includes OFF context for the current turn without blocking the host or rewriting saved mode. |
| Valid but invented classification detail could change emotion | Non-talk detail must be a nonempty verbatim span from the user's message. Invented grievance regression passes. This does not eliminate all semantic classification mistakes. |
| `/sai memories`/empty off crashed chat output | Render command result by type; list and None result regressions pass without model calls. |
| Slash parsing consumed quotes/backslashes | Parse command structure only; free-text tail is retained literally. Path/apostrophe/quotation regressions pass. |
| List showed ON after off | Read activation from metadata and mark inactive characters OFF. Regression passes. |

Full local suite after correction: **53 tests PASS**, Python 3.13.13 / Windows. No claim of a second independent review. Installed-package and real-model results are linked in the verification index.
