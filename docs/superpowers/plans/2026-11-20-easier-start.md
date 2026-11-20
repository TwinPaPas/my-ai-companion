# Easier Start 0.1.2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Ship guided standalone startup, concise everyday dialogue, and an honest real-dialogue demonstration.
**Architecture:** A focused onboarding module coordinates existing Store, backend resolution and run_chat. Shared context guidance sets conversational style without changing engine state or adding calls.
**Tech Stack:** Python 3.11+, unittest, existing SQLite and CLI backends; Pillow/FFmpeg for development-only media.
**Spec:** docs/superpowers/specs/2026-11-20-easier-start-design.md

## Global Constraints

English runtime and retained Korean docs; no runtime dependencies, DB migration, host trust/config edits, implicit memories, new schedule or invented adoption. Preserve old releases/evidence. Hidden subprocesses, serial model calls, at most two low-priority encoder threads.

## Review Focus

- Cancellation or invalid setup must not create a half-configured character or enable an existing OFF character.
- Missing/invalid backend override must fail before state mutation; executable detection is not authentication proof.
- Selecting another existing character must preserve both characters' memories and avoid defaulting to the wrong one.
- A short-response instruction must not erase unresolved concern or suppress a requested substantive work answer.
- Installed startup must work outside the source tree, with Unicode names and interpreter paths containing spaces.

### Task 1: Guided start

**Files:** create sai/onboarding.py and tests/test_onboarding.py; modify sai/cli.py.
**Interfaces:** consume Store.list/status/create/use, resolve_executable(host), run_chat(store, host); produce start(store, backend=None) -> int.

- [x] Add behavioral tests for setup and persisted state, selection/resume, cancellation, invalid answers, missing backends and JSON rejection. Run `python -B -m unittest discover -s tests -p test_onboarding.py -v`; expect feature-missing failures.
- [x] Implement guided selection with create/use only after complete valid input; call existing run_chat. Register `start --backend` and reject JSON before prompts.
- [x] Run `python -B -m unittest discover -s tests -v`; expect all tests passing. Commit the focused feature and tests.

### Task 2: Dialogue and everyday capture

**Files:** modify sai/context.py; create scripts/capture_everyday.py and scripts/render_everyday.py; record evidence under docs/verification.
**Interfaces:** use Task 1's start route in package checks; capture calls existing CLI chat and stores full real replies.

- [x] Record the baseline using an isolated character with explicit memory, conflict/apology state and neutral everyday prompts. Evaluate the stated 80-word/recall/topic criteria and preserve FAILs.
- [x] Add shared concise, topic-sensitive style guidance. Run the full suite; capture the same real Claude scenario and a Codex casual/recall sample. Require the defined checks and review full dialogue for accurate state and relevant answers. Codex's additional strict English-only check remains FAIL for the host honorific; the separate memory/brevity checks passed, as recorded in the ledger.
- [x] Render exact reply excerpts as a labelled 30-second edited playback. Validate quote provenance, duration, dimensions and inspect the contact sheet. Commit source and textual evidence; media stay release assets.

### Task 3: Package and publication

**Files:** modify pyproject.toml, sai/__init__.py, sai/cli.py version, README.md, README.en.md, README.ko.md, scripts/verify_package.py, scripts/verify_english.py, docs/verification/README.md, HANDOFF.md; add docs/releases/0.1.2.md.
**Interfaces:** installed start -> existing chat; actual capture -> media/release/README.

- [x] Set version 0.1.2 and document one guided command, honest detection/login limits, English-first defaults and preserved manual commands.
- [x] Build wheel and verify isolated installed startup (Unicode/path spaces), state, OFF and hooks; observe real Claude native context/OFF. Keep native Codex activation unverified.
- [x] Run final suite and entry-document/link checks. Get one fresh whole-branch code review, fix material findings with regression tests, then integrate into C:\ai_sai.
- [x] Push authorized release code, wait for CI, publish v0.1.2 with wheel and everyday media, verify hashes/public text and retain a concise handoff. Preserve failures.
- [ ] Clean only task-owned temporary output — release artifacts are now in `C:\ai_sai\dist` with matching hashes and review records are backed up on E:. Temporary-directory deletion remains BLOCKED before execution by automatic approval review, including the follow-up after the owner's explicit cleanup request; see docs/progress-0.1.2.md.
