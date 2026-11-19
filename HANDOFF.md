# SAI handoff — 2026-11-20 (KST)

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
