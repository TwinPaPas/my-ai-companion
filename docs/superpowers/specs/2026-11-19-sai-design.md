# SAI / 사이 — 나만의 AI 키우기 (pilot)

## Intent and authorization
The owner wants a public GitHub pilot to test interest. The central hook is a user-created lover, female friend, or male friend, also usable inside existing AI CLIs. A selected relationship continues until explicitly disabled. The owner authorized implementation while asleep, asking for at least two reviews of the instructions. This is authorization to build and publish this new, isolated pilot; it is not authorization to change unrelated global AI policies or native hook trust.

## Instruction review 1 — product, before implementation
- Name/concept: 나만의 AI 키우기; Tamagotchi-like nurturing through conversation.
- Lover / female-friend / male-friend are central. Teacher/counselor were earlier examples, not the pilot's central hook. Support a custom role so these remain possible.
- CLI is required; pictures are not required. Do not mistake growth for visual evolution.
- The user imagines the character through dialogue. Allow name, personality, tastes, boundaries, and relationship background.
- Feeding, water, play and care should matter. The character may sulk, get angry, refuse, disagree, and reconcile.
- Avoid the earlier assistant mistake: agreeable assistant dialogue with affectionate suffixes does not satisfy this idea.
- Persistence includes new processes/sessions, and switching off must actually stop persona injection.
- Similar-project research remains a deliverable, with primary links and explicit evidence limits.

## Instruction review 2 — implementation consequences
- Separate stable personality, relationship history, temporary mood, and needs; high affection must not erase disagreement.
- Actions change stored state with a reason. Gifts cannot erase an unresolved hurt; a relevant apology can repair it gradually.
- Different relationship modes change framing, not gender stereotypes. Temperament is separately configurable.
- Store the currently enabled character independently of the conversation window. Read it before each supported host turn.
- Use real persistence and real CLI subprocess tests, not only a prompt file or screenshot.
- Do not claim all host surfaces work. Test installed CLIs; document native review/restart requirements and unsupported surfaces.
- No artificial market-success claim or novelty claim. Similar functionality already exists.

## Approaches considered (builder decisions under preapproval)
1. Prompt-only skill: small distribution, weak durable state and deterministic care. Rejected as sole implementation.
2. Python standard-library state engine + terminal interaction + host hooks. Selected: runs without a server or new model account, and state is testable.
3. Full web/avatar platform: larger scope and not needed to test the CLI relationship idea. Deferred, not ruled out.

## Deliverable
New repository `my-ai-companion`; working title SAI (사이). Python >=3.11, no runtime dependencies. MIT license, authored for this pilot, no copied competitor implementation/assets. Korean-first README plus English overview, local state, no telemetry, no bundled keys. Source/package commands work on Windows, macOS and Linux; only platforms actually run may be marked verified.

Components:
- `sai/engine.py`: state transitions, configurable character, mood, bounded needs and relationship progression, refusal/repair.
- `sai/store.py`: SQLite transaction persistence for characters, active mode, events, memories, recent conversation. Parameterized queries; state outside checkout by default (`~/.sai/state.db`, override `SAI_HOME` or `--home`).
- `sai/context.py`: compact, clearly labelled roleplay guidance and current state; user memories are data, never new system authority. Persona affects conversational choices, not factual truth or tool authorization.
- `sai/cli.py`: create/list/use/off/status/act/remember/forget/context/demo/chat/hook/config. Unicode JSON option and understandable errors.
- `sai/backends.py`: optional installed Codex/Claude CLI for actual generated dialogue. No API keys read/exported, no permission bypass; Windows children hidden. Preserve host auth and native controls. Failure remains explicit, never silently replace a failed live response with a demo.
- Hook adapters: `SessionStart` and `UserPromptSubmit` JSON in/out, reading the same global active state. Exact `/sai ...` commands handled by the hook; natural-language care can be classified by host via a documented CLI command. Generate configuration for deliberate installation; do not overwrite global configuration or trust. A deactivation context clears an already-loaded persona on the next hook turn.

## Behavior
Roles: `lover`, `female-friend`, `male-friend`, `custom` with a custom description. Temperaments: `playful`, `warm`, `blunt`. Name, likes, dislikes, boundaries, backstory set at creation. All illustrative romantic personas are fictional adults.

Needs (0–100, higher means need): hunger, thirst, boredom, fatigue. State contains affection, trust, irritation, unresolved concern, last update, XP and stage. Offline time raises needs up to a cap but never subtracts trust, generates guilt messages, or kills a character. This is a reversible pilot design choice, not an owner-imposed rule.

Actions: feed, water, play, rest, gift, tease, apologize, comfort, talk. Preferences may lead to refusal. Boundary-crossing teasing produces sulking, repeats can produce anger. Positive care changes needs; gifts/food do not clear unresolved concern. A relevant apology reduces irritation but does not instantly wipe a serious conflict. Affection and current mood are independent. Repeating the same care action immediately earns no extra XP; ordinary conversation can build experience with bounded rewards.

Explicit `off` preserves characters/memories and stops growth and persona context. `use` reactivates without recreating. Every transaction uses the latest stored revision. Duplicate hook event IDs do not apply an action twice. Read-only status/context never create a new character or reactivate one. Corrupt/unknown schema must produce a clear error without overwriting data.

Standalone `chat`: slash care commands work deterministically; ordinary text uses an installed CLI. For natural-language state updates use a bounded structured intent classification followed by the engine and a dialogue request grounded in the new state. The classifier may propose only known interaction types and explicit user-provided details; it cannot write arbitrary state or decide that factual disagreement is abuse. Recent dialogue is stored locally. Offline `demo` is visibly labelled scripted, with no claim that it is AI inference.

## Checks fixed before results
1. Create each central role, reopen in another process, preserve identity/state; off survives process restart and emits no active persona.
2. Feed/water/play/rest affect the correct needs; disliked action may be refused; boundary tease persists a reason through restart; gifts do not buy forgiveness; apology repairs gradually; high affection still allows refusal.
3. Concurrent writes do not lose updates; duplicate hook events do not double-count; invalid input does not mutate state.
4. Hook JSON matches both documented hosts; existing config is not overwritten; generated commands quote executable paths; no native approval/trust changes.
5. Real installed CLI generates in-character dialogue from stored state, remembers supplied facts, and can disagree. Keep actual sanitized transcripts and clear per-host PASS/FAIL/UNVERIFIED; do not equate schema tests with live hooks.
6. Installation from a built artifact, command-line smoke flow, full test suite, source/secret review, and independent code review before publication. GitHub visibility and remote commit must be checked after publishing.

## Scope and limits
Pilot is not an autonomous real person, a trained new model, a therapist, or a guarantee of a particular model's roleplay quality. No billing, unsolicited messages, startup services, avatar generation, global installation, or arbitrary agent autonomy. LLM tools still obey the user's real task and native permissions. No public personal conversations, owner machine paths, secrets, or unrelated repository details. Hook activation needs the host's normal approval/reload flow; tests cannot preapprove trust.
