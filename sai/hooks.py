"""Non-blocking JSON lifecycle hooks; installation remains explicit."""
import hashlib
import json
import shlex
import os
from pathlib import Path
import sys

from .context import build_context, OFF_CONTEXT


def hook_config(host):
    if host not in ("codex", "claude"):
        raise ValueError("host must be codex or claude")
    executable = str(Path(sys.executable).absolute())
    if host == "claude":
        handler = {"type": "command", "command": executable, "args": ["-I", "-m", "sai", "hook"], "timeout": 5}
    else:
        # Codex runs through its host shell. Windows config targets PowerShell.
        command = ("& '" + executable.replace("'", "''") + "'" if os.name == "nt" else shlex.quote(executable))
        handler = {"type": "command", "command": command + " -I -m sai hook", "timeout": 5}
    return {"hooks": {event: [{"hooks": [dict(handler)]}]
                      for event in ("SessionStart", "UserPromptSubmit")}}


def parse_command(text):
    """Slash commands are not shell programs; preserve free-text bytes and quotes."""
    if "\n" in text or "\r" in text:
        raise ValueError("SAI commands must be a single line")
    parts = text.strip().split(None, 2)
    if len(parts) < 2 or parts[0] != "/sai":
        raise ValueError("Expected /sai COMMAND")
    command = parts[1]
    if len(parts) == 2:
        return [command]
    rest = parts[2]
    if command == "remember":
        return [command, rest]
    if command == "act":
        return [command, *rest.split(None, 1)]
    return [command, *rest.split()]


def execute_command(words, store, event_id=None, expected_character_id=None):
    if not words:
        raise ValueError("Use /sai status, off, use ID, act ACTION DETAIL, remember TEXT, memories or forget ID")
    command, *args = words
    if command == "off" and not args:
        return store.off(event_id=event_id)
    if command == "status" and not args:
        return store.status()
    if command == "use" and len(args) == 1:
        return store.use(args[0], event_id=event_id)
    if command == "act" and args:
        return store.act(args[0], " ".join(args[1:]), event_id=event_id, expected_character_id=expected_character_id)
    if command == "remember" and args:
        return store.remember(" ".join(args), event_id=event_id)
    if command == "memories" and not args:
        return store.memories()
    if command == "forget" and len(args) == 1:
        return store.forget(args[0], event_id=event_id)
    raise ValueError("Unknown SAI command or arguments")


def handle_hook(payload, store):
    if not isinstance(payload, dict):
        return {"systemMessage": "SAI: invalid hook input; persona was not updated."}
    event = payload.get("hook_event_name")
    if event not in ("SessionStart", "UserPromptSubmit"):
        return {}
    try:
        prefix = ""
        result = None
        if event == "UserPromptSubmit":
            prompt = payload.get("prompt", "")
            if not isinstance(prompt, str) or len(prompt) > 100000:
                raise ValueError("invalid prompt")
            if prompt.strip().startswith("/sai "):
                if "\n" in prompt.strip():
                    raise ValueError("SAI commands must be a single line")
                event_id = None
                if payload.get("turn_id") or payload.get("event_id"):
                    raw = json.dumps([payload.get("session_id"), payload.get("turn_id") or payload["event_id"], prompt])
                    event_id = "hook-" + hashlib.sha256(raw.encode()).hexdigest()
                result = execute_command(parse_command(prompt), store, event_id)
                # A replay can refer to a previously selected character. Never inject its data.
                prefix = "SAI command handled; do not repeat it. Use the CURRENT snapshot below.\n"
                if isinstance(result, dict) and result.get("duplicate"):
                    prefix += "This was a duplicate delivery; no state changed.\n"
        snapshot = store.snapshot()
        state = snapshot["state"]
        context = build_context(state, snapshot["memories"], store.home)
        if (isinstance(result, dict) and "state" in result and not result.get("duplicate")
                and state and result["state"]["id"] == state["id"]):
            prefix += "Action result (data): " + json.dumps({k: result[k] for k in
                ("action", "detail", "accepted", "reason", "mood")}, ensure_ascii=False) + "\n"
        if state and not state["enabled"]:
            prefix = ""
        if not context and not prefix:
            return {}
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": prefix + context}}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never block a user's real coding task for a companion failure.
        return {"systemMessage": "SAI hook failed: " + str(exc),
                "hookSpecificOutput": {"hookEventName": event, "additionalContext": OFF_CONTEXT +
                    "\nSuspend roleplay for this turn because current state could not be applied. Saved mode is unchanged by this error."}}
