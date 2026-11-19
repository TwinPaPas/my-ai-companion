# English pilot implementation plan

> **For agentic workers:** Use executing-plans for the remaining artifact and publication work. The owner has authorized this scope; no repeated approval is needed.

**Goal:** Publish an English-first SAI pilot with warmer copy, a truthful short demonstration, a small user-study kit and a ready handoff.

**Architecture:** Keep the existing CLI and state engine. Translate presentation strings. Capture separate real CLI processes into JSON, then render the exact replies as an explicitly edited playback.

**Tech Stack:** Python 3.11+, SQLite, existing Claude/Codex CLIs; Pillow/imageio-ffmpeg only for optional media generation.

**Spec:** `docs/superpowers/specs/2026-11-20-english-pilot-design.md`.

## Constraints and review focus

- No new runtime dependencies or state-schema changes; preserve Unicode names/memories.
- Never label scripted lines or edited timing as live inference/real-time footage.
- Native Codex hook remains unverified; no trust changes.
- Do not invent recruitment, retention results or scheduled monitoring.
- Keep public docs English by default and retain Korean guides. Final checkout: `C:\ai_sai`.

## Tasks

- [x] Translate README, CLI/help, action explanations and demo; warm Korean/English introduction. Existing 53-test suite passed after code string changes.
- [x] Capture real English Claude dialogue across fresh processes using `scripts/capture_showcase.py`; save full stdout/replies, return codes and before/after state checks to `docs/verification/showcase-0.1.1.json`.
- [x] Render `dist/sai-0.1.1-showcase.mp4` and preview GIF from that evidence with `scripts/render_showcase.py`; verify 30-second duration and inspect scene frames.
- [x] Put native integration status and clip above installation; add `docs/PILOT.md` plus voluntary feedback form and English release notes.
- [x] Build and verify 0.1.1 wheel; existing 53-test suite and link/language checks PASS. Additional independent review omitted under the owner's later instruction to skip nonessential stages; this is explicitly disclosed in HANDOFF.md.
- [x] Merge, publish source/release, check CI and remote artifact hashes; create working checkout at requested path and write handoff with actual completed/pending items.
