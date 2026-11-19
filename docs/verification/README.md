# Verification — SAI pilots

## 0.1.1 English interface and demonstration

- Existing suite: 53 tests passed after presentation-string changes; no state schema or mechanics changes.
- [Showcase capture](showcase-0.1.1.json): real English Claude replies. Each CLI command ran in a separate process, and the stored identity/concern survived chat exit. A new generated reply recalled the conflict; flowers did not clear it; an apology reduced irritation.
- [Render evidence](showcase-render-0.1.1.json): 30-second 1600×900 MP4 plus GIF. This is an **edited terminal-style playback of exact reply excerpts**, not a real-time screen recording. All six scene frames were visually inspected for readability and overflow. The capture retains full replies.
- [Package check](package-0.1.1.json) records the new wheel's installed CLI checks and digest. Historical checks below remain associated with 0.1.0.
- Participants have not yet been recruited and next-day use has not been observed. [Pilot protocol](../PILOT.md). The quoted daily-check schedule is unverified.

## 0.1.0 baseline

Pilot verification results. Tests verify mechanics and process integration; they do not establish that the relationship is enjoyable over time.

- Local unit/process suite: **53 tests PASS** on Python 3.13.13 / Windows, including the independent review's regression cases. [Review and corrections](review.md).
- [GitHub CI result](ci.json): Windows and Ubuntu, Python 3.11 and 3.13, all four jobs passed tests, installation and demo on release code `4f31431`. [Run](https://github.com/TwinPaPas/my-ai-companion/actions/runs/44549872088).
- [Claude live transcript](live-claude.json): actual generated dialogue, natural food refusal, persistent anger, gift without instant forgiveness, gradual apology, explicit memory recall. Native hook on/off also observed with session-local settings and isolated state.
- [Codex live transcript](live-codex.json): actual intent classification and generated refusal PASS. The existing host's honorific instruction affected the character's address; personality requests do not override host instructions. Native Codex hook activation remains unverified and trust is not preapproved or bypassed.
- [Final Claude check](final-claude.json) and [final Codex check](final-codex.json): after the corrections, real intent classification with verbatim evidence and generated disliked-food refusal PASS in both backends.
- [Package check](package.json): corrected wheel installed into a temporary venv and exercised outside the checkout; three central roles, restart persistence, off and demo PASS. Generated hook commands worked with a spaced interpreter path, Korean UTF-8 input and a shadow cwd module. **Real Claude native hooks using the installed wheel supplied context and OFF.** Codex's generated command was exercised through PowerShell; its native hook activation remains UNVERIFIED.
- [Release source check](release-check.json): heuristic credential/runtime-artifact scan. It does not guarantee the absence of all sensitive information.
- [Public v0.1.0 prerelease](https://github.com/TwinPaPas/my-ai-companion/releases/tag/v0.1.0): uploaded wheel SHA-256 matches `package.json` (`c14652045cfd917cddd22eaeaf858d1474551054b0606ad6e4c36f4c344e0a1c`). Public visibility, main branch and the uploaded asset were checked through GitHub after publication.
- `demo-transcript.json` in the parent directory is scripted dialogue plus actual engine state, not live inference.

Subjective review of the first Claude transcript: tastes and anger were expressed distinctly; replies tended to be long and sometimes repeated the grievance. No claim of calibrated human emotion, long-term user satisfaction, or model-independent consistency.

The classifier must quote a span present in the message before applying a non-talk action. It can still misunderstand semantics; explicit `/sai act ...` avoids classification. Native host instructions can affect honorifics/style. No global host configuration or trust state was modified for verification.

Initial FAILs are retained in `docs/progress.md`. No personal state, keys or existing user conversations are included in these artifacts.
