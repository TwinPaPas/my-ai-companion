# SAI — English quick start

A sweetheart to fall for. A girl best friend or a guy best friend to laugh with. Give them a name and tell them about your day. With a little teasing, a little sulking and a few awkward apologies, ordinary conversations become a story that's yours.

[Full English guide](README.md) · [한국어](README.ko.md)

**Early pilot.** Python 3.11+, no runtime dependencies. A local state engine controls needs, mood, trust and growth; an installed Claude Code or Codex CLI generates dialogue. No avatar required.

```sh
git clone https://github.com/TwinPaPas/my-ai-companion.git
cd my-ai-companion
python -m pip install .
python -m sai demo
python -m sai create Ari --role male-friend --temperament blunt --like tea --dislike cucumber --boundary appearance
python -m sai act water
python -m sai chat --backend claude
```

`demo` uses **scripted dialogue and the real engine**, with no model calls or persistent user state. Live chat requires an installed, authenticated CLI. Natural-language chat usually makes two calls (intent + dialogue); explicit `/sai act ...` makes one. Your provider's usage applies. Failures never silently turn into demo replies.

Roles: `lover`, `female-friend`, `male-friend`, `custom` (requires `--backstory`). Temperament is separately chosen: `playful`, `warm`, `blunt`. Repeat `--like`, `--dislike`, `--boundary` to personalize. All romantic example characters are fictional adults.

```text
/sai act feed tea
/sai act play word-game
/sai act tease appearance
/sai act gift flowers
/sai act apologize I am sorry for teasing your appearance
/sai remember I like blueberry pie
/sai status
/sai off
/quit
```

Disliked offers may be refused even at high affection. Repeated boundary-crossing teasing causes anger; gifts do not erase an unresolved hurt. Relevant apologies repair gradually. Absence never costs trust or kills a character. `/quit` closes chat; **`/sai off` disables the role** while preserving data.

State defaults to `~/.sai/state.db`. Override `SAI_HOME` or use `python -m sai --home PATH ...`. `list`, `use ID`, `memories`, `forget ID`, and `off` manage characters and memory. The active choice and enabled flag survive new processes and directories. Global flags `--home` and `--json` go before the subcommand.

`python -m sai config claude` / `config codex` print hook configuration only. [Integration details](docs/INTEGRATION.md) explain merging it without replacing existing hooks. Native trust/reload still applies. Permissions and real task correctness are not controlled by a character's mood.

Data stays in local SQLite until used for inference: selected memories, character state, recent dialogue and current text are sent to the chosen AI provider through its CLI. There is no SAI telemetry. Recent context is bounded (8 dialogue pairs, 12 explicit memories). This is not model training or a claim of sentience.

[Prior art](docs/research.md) · [Verification and limitations](docs/verification/README.md) · [Feedback](https://github.com/TwinPaPas/my-ai-companion/issues/new/choose)

```sh
python -m unittest discover -s tests -v
python -m pip wheel . --no-deps --wheel-dir dist
```

MIT License.
