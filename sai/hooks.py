"""Non-blocking JSON lifecycle hooks; installation remains explicit."""
import hashlib
import json
import shlex

from .context import build_context


def hook_config(host):
    if host not in ("codex", "claude"):
        raise ValueError("host must be codex or claude")
    return {"hooks": {event: [{"hooks": [{"type": "command", "command": "python -m sai hook",
                                          "timeout": 5}]}]
                      for event in ("SessionStart", "UserPromptSubmit")}}


def execute_command(words, store, event_id=None):
    if not words:
        raise ValueError("Use /sai status, off, use ID, act ACTION DETAIL, remember TEXT, memories or forget ID")
    command, *args = words
    if command == "off" and not args:
        return store.off()
    if command == "status" and not args:
        return store.status()
    if command == "use" and len(args) == 1:
        return store.use(args[0])
    if command == "act" and args:
        return store.act(args[0], " ".join(args[1:]), event_id=event_id)
    if command == "remember" and args:
        return store.remember(" ".join(args))
    if command == "memories" and not args:
        return store.memories()
    if command == "forget" and len(args) == 1:
        store.forget(args[0])
        return {"forgotten": args[0]}
    raise ValueError("Unknown SAI command or arguments")


def handle_hook(payload, store):
    if not isinstance(payload, dict):
        return {"systemMessage": "SAI: invalid hook input; persona was not updated."}
    event = payload.get("hook_event_name")
    if event not in ("SessionStart", "UserPromptSubmit"):
        return {}
    try:
        prefix = ""
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
                result = execute_command(shlex.split(prompt.strip())[1:], store, event_id)
                prefix = "SAI command was already applied. Do not repeat it. Result (data):\n" + json.dumps(result, ensure_ascii=False) + "\n"
        state = store.status()
        context = build_context(state, store.memories())
        if state and not state["enabled"]:
            prefix = ""
        if not context and not prefix:
            return {}
        return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": prefix + context}}
    except (ValueError, OSError, KeyError, TypeError) as exc:
        # Never block a user's real coding task for a companion failure.
        return {"systemMessage": "SAI hook failed; no persona update: " + str(exc)}
