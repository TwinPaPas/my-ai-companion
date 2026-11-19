# SAI 0.1.0 — first public pilot

Grow a fictional relationship in your CLI: a sweetheart, a girl best friend or a guy best friend with their own tastes, moods and memories.

- Configure temperament, tastes and background independently of relationship mode.
- Care, refusal, sulking, anger and gradual reconciliation persist in local state.
- Keep the selected character until `off`, with separate memories and dialogue for each character.
- Generate real dialogue through an installed Claude Code or Codex CLI. Your provider's usage applies.
- Print host hook configuration. Claude native hooks were observed; native Codex activation remains unverified. Codex Windows configuration targets PowerShell.

Install from source: `python -m pip install .`

Install the original wheel: `python -m pip install sai_companion-0.1.0-py3-none-any.whl`

Try `python -m sai demo`: scripted dialogue with the real state engine, without model calls.

Verified 53 automated tests, actual disliked-food refusal in both backends, package installation and Claude hook ON/OFF. Evidence and initial failures are retained in `docs/verification/` and `docs/progress.md`.

This is an early pilot. Replies may become long or repetitive and intent classification can be wrong. Share fictional examples of sweet, funny or awkward reactions through GitHub Issues.

**Historical release:** the 0.1.0 wheel has Korean CLI messages. Use [0.1.1](https://github.com/TwinPaPas/my-ai-companion/releases/tag/v0.1.1) for the English interface and the real-dialogue showcase.
