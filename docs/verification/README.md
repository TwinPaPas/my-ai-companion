# Verification — pilot 0.1.0

Pilot verification results. Tests verify mechanics and process integration; they do not establish that the relationship is enjoyable over time.

- Local unit/process suite: **53 tests PASS** on Python 3.13.13 / Windows, including the independent review's regression cases. [Review and corrections](review.md).
- [Claude live transcript](live-claude.json): actual generated dialogue, natural food refusal, persistent anger, gift without instant forgiveness, gradual apology, explicit memory recall. Native hook on/off also observed with session-local settings and isolated state.
- [Codex live transcript](live-codex.json): actual intent classification and generated refusal PASS. The existing host's honorific instruction affected the character's address; personality requests do not override host instructions. Native Codex hook activation remains unverified and trust is not preapproved or bypassed.
- [Final Claude check](final-claude.json) and [final Codex check](final-codex.json): after the corrections, real intent classification with verbatim evidence and generated disliked-food refusal PASS in both backends.
- [Package check](package.json): corrected wheel installed into a temporary venv and exercised outside the checkout; three central roles, restart persistence, off and demo PASS. Generated hook commands worked with a spaced interpreter path, Korean UTF-8 input and a shadow cwd module. **Real Claude native hooks using the installed wheel supplied context and OFF.** Codex's generated command was exercised through PowerShell; its native hook activation remains UNVERIFIED.
- [Release source check](release-check.json): heuristic credential/runtime-artifact scan. It does not guarantee the absence of all sensitive information.
- `demo-transcript.json` in the parent directory is scripted dialogue plus actual engine state, not live inference.

Subjective review of the first Claude transcript: tastes and anger were expressed distinctly; replies tended to be long and sometimes repeated the grievance. No claim of calibrated human emotion, long-term user satisfaction, or model-independent consistency.

The classifier must quote a span present in the message before applying a non-talk action. It can still misunderstand semantics; explicit `/sai act ...` avoids classification. Native host instructions can affect honorifics/style. No global host configuration or trust state was modified for verification.

Initial FAILs are retained in `docs/progress.md`. No personal state, keys or existing user conversations are included in these artifacts.
