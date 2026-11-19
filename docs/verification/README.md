# Verification — pilot 0.1.0

Verification is still being completed on the implementation branch. This file will be finalized before release.

- Local unit/process suite: 41 tests PASS on Python 3.13 / Windows at the last implementation run.
- [Claude live transcript](live-claude.json): actual generated dialogue, natural food refusal, persistent anger, gift without instant forgiveness, gradual apology, explicit memory recall. Native hook on/off also observed with session-local settings and isolated state.
- Codex live run: pending. Codex native hook trust is not preapproved or bypassed by these scripts.
- [Package check](package.json): script installs the wheel into a temporary venv and runs outside the checkout; result is recorded by execution.
- `demo-transcript.json` in the parent directory is scripted dialogue plus actual engine state, not live inference.

Subjective review of the first Claude transcript: tastes and anger were expressed distinctly; replies tended to be long and sometimes repeated the grievance. No claim of calibrated human emotion, long-term user satisfaction, or model-independent consistency.

Initial FAILs are retained in `docs/progress.md`. No personal state, keys or existing user conversations are included in these artifacts.
