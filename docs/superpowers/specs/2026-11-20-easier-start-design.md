# Easier first conversation and everyday dialogue — 0.1.2

The owner approved the recommendation to improve first-run setup and dialogue quality, add an everyday-use demonstration, and publish the next pilot. This is the implementation of that approval; no further design or deployment approval is required within this scope.

## Approach and limits

Add `sai start [--backend claude|codex]` as a guided entry to the existing standalone chat. Reuse the store, executable resolver, and chat loop. Probe executable availability without a model call; explicitly say that login is checked on the first live reply. If both CLIs are available, ask which to use. Missing CLI errors identify the remedy before creating state. Never edit host configuration or trust settings.

Offer existing characters with the active one as default, plus a new-character choice. Creating a character asks for name, relationship, temperament, one optional like and dislike. Validate before writing. EOF/cancellation before the final create/use leaves existing state untouched. Resuming an OFF character explicitly turns it on, and the menu says so. `--json start` is rejected without prompts or state mutation; scripted users already have create/use/chat. No database migration, implicit memory capture, or provider/login automation.

Use one shared context instruction for casual dialogue: default to 1–3 concise sentences, one brief gesture at most, answer the current message, vary phrasing, and avoid bringing an old grievance into an unrelated topic. Stored concern, dislike and boundaries remain intact; a gift never erases them. Longer replies remain available when requested or needed for real work. Do not truncate generated text or add a second rewriting model call.

Alternatives considered: documentation-only onboarding is smaller but leaves the command/options barrier; a guided CLI directly addresses it without a new UI stack; web/avatar work expands the product without adoption evidence. Chosen: guided CLI plus shared dialogue guidance. Older-memory retrieval is deferred from this approved release recommendation. Native Codex activation remains unverified unless actually observed; no trust settings are changed.

## Verification defined before results

- New-start tests exercise the real store and chat loop with only external model/executable discovery replaced. Verify create/resume/switch, preserved memories, invalid answers, EOF before mutation, no available backend, explicit backend, and JSON rejection.
- Keep the existing 53 state/hook/backend tests; reuse the prior successful baseline because code at 5d7b033 is unchanged. Run the full suite after implementation.
- Before changing dialogue guidance, record a real Claude baseline with the same casual-topic scenario used after the change. Record failures rather than selecting or editing replies. For the post-change casual English sample, require at most 80 words per reply, correct explicit memory recall after a fresh process, and no reopening of the appearance grievance in neutral work/food questions after apology. This is a small observed sample, not a guarantee or adoption threshold.
- Verify a real Codex standalone casual reply and preservation of explicit memory; retain host style constraints. Keep mechanics assertions separate from subjective warmth/repetition review.
- Publish an edited 30-second everyday-use playback of exact real replies, labelled with waiting-time compression and standalone route. Preserve complete replies, timings, subprocess exits, and failed attempts. No fabricated screens, users, retention or real-world activity claims.
- Install the new wheel outside the checkout in a path with spaces; exercise start, persistence/OFF, and existing hook contracts. Confirm live Claude context/OFF because shared guidance changed. Validate media visually and public asset hashes, CI and links.

English remains the runtime/public default; Korean guidance is retained. Python >=3.11, standard-library runtime, serial model calls, hidden subprocess windows and low-priority media encoding with at most two threads. Keep previous releases/evidence. No new schedule, outreach to unspecified communities, or telemetry.
