# Use SAI with your AI CLI

[한국어](INTEGRATION.ko.md)

SAI provides two ways to chat:

1. `python -m sai chat --backend claude` or `--backend codex`: SAI prepares state and context for each turn and calls the installed model CLI.
2. `SessionStart` / `UserPromptSubmit` hooks: add your current character to the CLI you already use. The host continues to handle real work and tools.

## Generate and merge the configuration

Install SAI into the Python environment you will keep using, then check `python -m sai status`.

```console
python -m sai config claude
python -m sai config codex
```

The generated configuration uses the **absolute path of the current Python interpreter** and `-I -m sai hook`. Isolated mode prevents a project's `sai.py`, `PYTHONPATH` or virtual-environment PATH from replacing the installed package. Generate the config using the Python where you ran `pip install .`; running successfully from the source checkout alone does not prove installation.

Claude configuration uses `command` plus `args` to launch directly without a shell. Use a Claude Code version supporting this exec form; native operation was verified on 2.1.328. On Windows, Codex configuration targets **PowerShell**. On macOS/Linux it targets a POSIX shell. Other Windows host shells are unverified. Regenerate the configuration after moving or removing the Python environment.

- Claude Code: user `~/.claude/settings.json` or project `.claude/settings.local.json`.
- Codex: user `~/.codex/hooks.json` or project `.codex/hooks.json`.
- **Do not replace your existing settings file.** Append the generated handlers to the two event lists under `hooks`. Do not add an identical handler twice.
- User configuration applies across projects; project configuration applies to that project.
- Codex requires its normal native review/trust flow through `/hooks`. SAI does not write trust hashes or bypass review. Existing sessions must reload the configuration before it can take effect.
- Install in one scope to avoid duplicate hooks.

## Behavior and switching off

Each supported event loads the saved active character. With no state store, the hook returns no character context. An exact `/sai act ...` command applies the interaction directly. Natural-language care requires the host model to follow the supplied instructions and call SAI; the hook itself makes no LLM request.

```console
python -m sai off
```

On the next input, `SAI_MODE=OFF` clears the earlier persona instructions. Saved data remains. This cannot retract a reply the model is already generating.

To uninstall the integration, remove **only the SAI handlers you added**, then restart the host. Preserve your other hooks.

## Verify the integration

Config generation, stdin/stdout contract tests and actual host execution are different checks. In a new session, ask for the character's name and a stored memory. Then run `sai off` in another terminal and confirm the next turn sees OFF. See the [verification record](verification/README.md) for what has actually been tested, including the unverified native Codex activation.

Mode changes affect every session sharing the same database. Set different `SAI_HOME` values for simultaneous characters. With a `turn_id` or `event_id`, a command and its result are recorded in one transaction; replaying it after switching characters does not apply it again. Without an event ID, a repeated message cannot reliably be distinguished from a duplicate delivery.

Free text after `/sai remember` and `/sai act` is literal, not shell syntax. For example, `/sai remember I'm learning jazz` preserves the apostrophe and needs no quotes. A command-processing error suspends roleplay for that turn and reports the problem without blocking real work or changing the saved mode.

Official references: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks). The links describe host interfaces; the verification record states SAI's tested scope.
