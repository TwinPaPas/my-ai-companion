# SAI — a little closer, one conversation at a time

**A relationship that grows with the AI you already use.**

A sweetheart to fall for. A girl best friend or a guy best friend to laugh with.
Give them a name. Tell them about your day. Get to know their little likes and dislikes.
There may be teasing, a little sulking, and a few awkward apologies along the way.
Over time, those ordinary conversations become a story that's yours.

[한국어](README.ko.md) · [CLI integration](docs/INTEGRATION.md) · [Similar projects](docs/research.md) · [Verification](docs/verification/README.md)

> **Early pilot.** SAI is a fictional character experience in your terminal. It saves relationship state locally and uses an installed AI CLI to generate dialogue. Long-term consistency and enjoyment still need user feedback. No avatar or server to set up.

## The terminal closes. Your story stays.

They remember tomorrow's presentation, notice a small win, and still have their own taste in snacks. A little company while you get on with your day.

[![30-second edited playback of real Claude dialogue](https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.2/sai-0.1.2-everyday.gif)](https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.2/sai-0.1.2-everyday.mp4)

[Watch/download the 30-second MP4](https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.2/sai-0.1.2-everyday.mp4) · [Full replies and process evidence](docs/verification/everyday-0.1.2-claude-verified.json) · [Earlier conflict-and-repair demonstration](https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.1/sai-0.1.1-showcase.mp4)

This is an **edited playback of real generated replies**, with excerpts and waiting time compressed. It uses standalone SAI chat through Claude Code, not a real-time screen recording of native hooks. Each command runs in a fresh process against the same isolated state.

| Integration | Actually verified |
|---|---|
| Claude Code | Standalone generated chat; native hook character/memory context and ON/OFF in the initial pilot |
| Codex CLI | Standalone generated chat; **native hook activation is not yet verified** |

Detailed versions, evidence and limits are in the [verification record](docs/verification/README.md). We are [inviting five CLI users](docs/PILOT.md) to learn what makes them return on their own; no retention result is claimed yet.

## Try it

Python 3.11 or later, plus an installed and signed-in Claude Code or Codex CLI:

```console
python -m pip install "https://github.com/TwinPaPas/my-ai-companion/releases/download/v0.1.2/sai_companion-0.1.2-py3-none-any.whl"
python -m sai start
```

Choose an available CLI, then create a companion or pick up with a saved one. Press Enter for suggested relationship/temperament choices; names and tastes are yours. Choosing a saved character turns SAI on and preserves their memories. Cancel setup with Ctrl+C before saving.

`start --backend claude` or `start --backend codex` chooses the CLI directly. Detection checks for an executable; login and connection are checked on your first live reply. Setup does not edit your AI CLI settings. No CLI yet? Run `python -m sai demo` for the offline example below.

`demo` uses **scripted dialogue and the actual state engine**. It makes no model calls and does not create a saved character.

```text
You > Here's some cucumber.
Ari > Cucumber? You know that's not my thing. How about spicy noodles?

You > (Repeat a joke about their appearance after they asked you to stop.)
Ari [angry] > I asked you to stop. I'm not laughing this time.

You > I brought you flowers.
Ari > The flowers are lovely. But we still need to talk about earlier.
```

These are sample lines. Live dialogue depends on the model and character.

## Meet your character

Prefer explicit commands or more customization? The original commands remain available:

```console
python -m sai create Ari --role female-friend --temperament playful --like "spicy noodles" --dislike cucumber --boundary appearance --backstory "An old friend who loves teasing but knows what she likes."
python -m sai status
```

| Choice | Options |
|---|---|
| Relationship | `lover`, `female-friend`, `male-friend`, or `custom` |
| Temperament | `playful`, `warm`, or `blunt` |
| Tastes | Repeat `--like` and `--dislike` for more preferences |
| Sensitive topics | Repeat `--boundary` to name topics they dislike being teased about |
| Your shared background | Describe it with `--backstory`; required for `custom` |

Temperament is independent of gender. Growing closer does not erase their tastes. Characters are fictional adults.

## Spend a little time together

```console
python -m sai act feed "spicy noodles"
python -m sai act water
python -m sai act play "word game"
python -m sai act rest
python -m sai act gift flowers
python -m sai act tease appearance
python -m sai act apologize "I'm sorry for teasing your appearance"
python -m sai remember "My favorite snack is blueberry pie"
```

Hunger, thirst, boredom and fatigue change independently. Your character can turn down a disliked food or decline to play when upset or tired. A gift does not erase an unresolved disagreement. Relevant apologies repair it gradually. Repeating the same action immediately does not grant unlimited experience. Time away never costs trust or kills the character.

For generated conversation, install and sign in to **Claude Code or Codex CLI**:

```console
python -m sai chat --backend claude
python -m sai chat --backend codex
```

Ordinary messages are classified into an interaction, applied by the state engine, then used to generate dialogue. This usually makes two model calls per message; `/sai act ...` makes one. **Your provider's usage applies.** A backend error is reported, never replaced with a scripted reply. If only dialogue generation fails, the care action already applied remains saved.

CLI instructions are in English. Generated conversations follow the language you use, subject to the host model's instructions. Existing names, preferences and memories are preserved in their original language.

Inside chat:

```text
/sai act water
/sai act tease appearance
/sai act apologize I'm sorry for teasing your appearance
/sai remember I'm preparing a presentation this week
/sai status
/sai off
/quit
```

Slash-command text is literal; it does not need shell quotes. `/quit` closes the chat window. **Use `/sai off` or `python -m sai off` to disable the character.**

## Pick up where you left off

```console
python -m sai list
python -m sai use CHARACTER_ID
python -m sai memories
python -m sai forget MEMORY_ID
python -m sai off
```

Your selected character and ON/OFF setting survive process restarts and changes of project folder. `off` keeps memories intact. Each character has separate tastes, concerns, memories and conversation history.

State is stored in `~/.sai/state.db`. Use `SAI_HOME` or `python -m sai --home PATH ...` for a separate store. Put `--home` and `--json` **before** the subcommand. Context includes the last 8 dialogue pairs and the latest 12 explicit memories; `memories` shows all stored memories. This does not retrain a model.

## Bring SAI into your usual AI CLI

```console
python -m sai config claude
python -m sai config codex
```

These commands **print configuration only**. Follow the [integration guide](docs/INTEGRATION.md) to merge it into existing hooks. Each supported session start and user turn then receives the current character context.

Codex requires native hook trust review. Generating configuration, testing its input/output, and observing the host run it are separate checks. SAI does not change permissions or safety settings. Character moods never justify damaging real work or reporting false results.

## Data and current limits

- State, memories and dialogue are stored in local SQLite. SAI has no telemetry server.
- In live chat, selected memories, character state, recent dialogue and the current message are **sent to your chosen AI service** through its CLI. That service's data settings still apply.
- Natural-language care in host hooks depends on the host using the CLI tool. `/sai act ...` is handled directly. Deduplication requires a host-supplied event ID.
- Natural-language classification can be wrong. Explicit action commands avoid classification.
- Mood and experience values are game mechanics, not measurements of human psychology. Passing tests does not prove the experience is fun.
- Avatars, a web app, unsolicited messages and payments are not implemented.

## Help shape the next version

Tell us [which moments felt sweet, funny or awkward](https://github.com/TwinPaPas/my-ai-companion/issues/new/choose). Include the relationship, temperament and CLI, and use a fictional conversation to reproduce it. Do not attach private chats, API keys or your state database.

Similar projects already exist. Our [research notes](docs/research.md) describe the overlap. This pilot explores how relationships, everyday care and making up feel alongside regular AI use.

```console
python -m unittest discover -s tests -v
python -m pip wheel . --no-deps --wheel-dir dist
```

MIT License.
