# SAI handoff — current release 0.1.2, 2026-11-20 (KST)

## Current status (supersedes the historical section below)

- Work from `C:\ai_sai`. Published pilot: https://github.com/TwinPaPas/my-ai-companion/releases/tag/v0.1.2
- Release code is `01b880a5d25f1a5e0b6afa2f2136c96a7ce3ba40`. A later evidence-only commit records publication; it does not change runtime code.
- `python -m sai start` guides CLI selection, new character creation or resuming a saved character, then opens standalone chat. It does not install/login to a model CLI or modify global hooks. Existing state, explicit memories and OFF behavior are preserved.
- Shared dialogue guidance now targets concise casual replies, avoids repeating an old grievance in unrelated topics, and permits requested detailed work. No automatic truncation, extra model rewrite, schema migration or older-memory retrieval was added.
- Tests: 65 PASS locally after the independent review fixes. All four Windows/Ubuntu × Python 3.11/3.13 CI jobs passed for the release: https://github.com/TwinPaPas/my-ai-companion/actions/runs/44745890783
- Installed wheel: guided Unicode setup, OFF/resume and memory preservation worked outside the checkout with a spaced interpreter path. Real Claude native character/memory context and OFF were observed. See `docs/verification/package-0.1.2.json`.
- Real Claude sample: five casual replies 29–49 words, explicit recall and unchanged concern; requested five-part detail remained available. Codex sample: English replies retained the host's Korean honorific, so the strict English-only check is FAIL; memory/brevity checks passed. Native Codex hook activation is still unverified. Do not flatten these into an all-backends PASS.
- New 30-second everyday MP4/GIF uses exact recorded prompt/reply excerpts, compressed waits and explicit standalone labelling. All six scenes were visually checked. Previous releases and failed captures remain available.
- `docs/verification/publication-0.1.2-20261120-223931.json` confirms public access, tag SHA, CI and matching hashes for all four anonymously downloaded assets. Those downloads are maintainer verification, not adoption.
- After the owner's explicit final-cleanup request, all four v0.1.2 deliverables were moved to `C:\ai_sai\dist`; their hashes match the published verification record, and the worktree copies are absent. The previous v0.1.1 deliverables remain intact.
- Temporary-directory cleanup remains BLOCKED: automatic approval review rejected both the original combined command and the later deletion-only command before execution with only `blocked by policy`. No alternate-tool deletion was attempted. Task-owned `build`, `sai_companion.egg-info`, `sai\__pycache__` and `.superpowers\sdd\2026-11-20-easier-start` remain in `C:\Users\Zion_21\.codex\worktrees\dc42\ai_sai`. The managed worktree remains host-owned.
- The pre-cleanup Git history is verified in `E:\blueurban_backup\sai-0.1.2-20261120\before-final-cleanup.bundle`. Four review records were preserved in that directory's `review-records` folder and SHA-256 compared before the blocked deletion.
- The prior GitHub performance snapshots remain local in `docs/verification/github-performance-*`; they were not published. There is no new participant/retention observation, external outreach, telemetry or schedule in this release.
- Implementation decisions, failed attempts and review resolutions: `docs/progress-0.1.2.md`. No unresolved product-code review finding remains; cleanup is blocked as described above.

Current next-session instruction: Read `C:\ai_sai\HANDOFF.md` and follow the owner's next concrete request. Reuse the recorded release checks where source is unchanged; preserve local performance evidence. Native Codex hooks and user adoption remain unverified. Do not bypass the cleanup policy block or change host trust settings.

---

# Historical 0.1.1 handoff — retained for evidence

## Working location and published state

- Continue in `C:\ai_sai`. This is an independent Git checkout, not a worktree linked to the old folder.
- Repository: https://github.com/TwinPaPas/my-ai-companion
- Release: https://github.com/TwinPaPas/my-ai-companion/releases/tag/v0.1.1
- Release code: `95748b1c6904bc994661a651fd2f0e9bcdfa6f6a`; branch `main`. This handoff is a later documentation-only commit.
- Recruitment: https://github.com/TwinPaPas/my-ai-companion/issues/1 — open; zero comments when checked. No participant or return result is claimed.
- The tested wheel, MP4, GIF and contact-sheet PNG are in local `dist/` and on the release. They are intentional deliverables, not temporary files. Their hashes match the published assets and verification records.

## Completed

- English main README, CLI help/status/chat prompts, care explanations, scripted demo, integration guide, issue forms and release notes. Korean guides remain in `README.ko.md` and `docs/INTEGRATION.ko.md`.
- Warmer introduction in both languages. The main positioning is a relationship that carries over with the AI CLI people already use.
- Native integration status appears before installation: Claude context/memory/OFF observed in the original pilot; Codex standalone observed, native hook activation unverified.
- A 30-second edited terminal-style playback of actual English Claude replies. Separate CLI processes demonstrate persistent conflict, a gift that does not erase it, and an apology that softens the response. Excerpts and compressed waiting time are explicitly labelled. This is not real-time screen footage or a Codex native-hook demo.
- A public five-user pilot invitation, voluntary issue form and manual next-day-return table. The owner confirmed participants must still be recruited.
- Old 0.1.0 release notes are now English and explicitly identify its historical Korean-interface wheel.

## Verified

- Existing suite: 53 tests passed after runtime string changes.
- GitHub CI: all four Windows/Ubuntu × Python 3.11/3.13 jobs passed for the release code: https://github.com/TwinPaPas/my-ai-companion/actions/runs/44615087827
- `docs/verification/package-0.1.1.json`: installed wheel worked outside the checkout, English demo, all three roles, persistence/OFF, generated hook commands, Unicode data, interpreter paths with spaces and cwd-shadow isolation.
- `docs/verification/showcase-0.1.1.json`: full actual generated replies, subprocess exit codes and state checks.
- `docs/verification/showcase-render-0.1.1.json`: 30.0 seconds, 1600×900, exact excerpt sources and media hashes. All six scene frames were visually inspected.
- `docs/verification/english-0.1.1.json`: English runtime source and local entry-document links passed.
- The first inline language check failed because of the console pipe's handling of its non-ASCII regex. The saved UTF-8 verification script passed. Details remain in `docs/progress.md`.

## Open questions and limits

- Recruit actual users and observe whether they voluntarily return the next day. No retention threshold or feature-expansion decision has been set.
- Native Codex hook activation remains unverified. No host trust/approval settings were modified.
- The supplied feedback claimed SAI was added to a daily development check; no schedule was verified or created here.
- No separate global package installation or global hook configuration was added. From this source checkout, `python -m sai demo` works; run `python -m pip install .` in the intended Python environment before generating installed hook configuration.
- Replies and intent classification can still be imperfect. Runtime/schema behavior was not redesigned in this release.
- The owner asked to skip nonessential steps. Existing successful checks were reused; no second independent reviewer was run for this presentation-focused update. The original pilot's review/corrections remain recorded.

## Next session

1. Read this file and the current recruitment issue. Record only real volunteers and voluntarily reported observations in the pilot record.
2. Keep the current English-first public presentation and preserve Korean documentation and prior raw evidence.
3. Work from the owner's next concrete request. Avatars, a web app, reminders and an automatic monitoring schedule were not part of the completed scope.

The English worktree and its local branch were removed after merge. The old `C:\my-ai-companion` checkout remains as the original working location; earlier ignored test caches there were left after an approval-review block. Do not confuse that older location with this handoff checkout or retry its blocked cleanup as part of the pilot work.

Suggested next-session prompt:

> Read `C:\ai_sai\HANDOFF.md`, confirm the published version and the five-user recruitment issue, and report actual new responses. Reuse existing verification where code has not changed. Do not alter host trust settings or expand into new features or schedules without a concrete request.
