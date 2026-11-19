from __future__ import annotations

import argparse
import json
import sys

from .context import build_context
from .demo import demo
from .engine import ACTIONS, ROLES, TEMPERAMENTS
from .hooks import handle_hook, hook_config
from .store import Store

ROLE_NAMES = {"lover": "Sweetheart", "female-friend": "Girl best friend", "male-friend": "Guy best friend", "custom": "Custom relationship"}
MOOD_NAMES = {"curious": "Getting to know you", "comfortable": "At ease", "sulking": "Sulking", "angry": "Angry", "tired": "Tired"}


def parser():
    p = argparse.ArgumentParser(prog="sai", description="SAI — your own AI companion, with tastes and a story to grow together")
    p.add_argument("--home", help="State directory (default: ~/.sai or SAI_HOME)")
    p.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    p.add_argument("--version", action="version", version="sai 0.1.1")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create", help="Create a character and start your story")
    c.add_argument("name")
    c.add_argument("--role", choices=ROLES, required=True)
    c.add_argument("--temperament", choices=TEMPERAMENTS, default="playful")
    for arg in ("like", "dislike", "boundary"):
        c.add_argument("--" + arg, action="append", default=[])
    c.add_argument("--backstory", default="")
    for command, help_text in [("list", "List your characters"), ("status", "See how your character is doing"), ("off", "Turn off roleplay, keeping memories"),
                               ("context", "Show the current character context"), ("memories", "Read saved memories"), ("demo", "Try a scripted demo without model calls"),
                               ("hook", "AI CLI lifecycle hook")]:
        sub.add_parser(command, help=help_text)
    sub.add_parser("use", help="Pick up with a saved character").add_argument("id")
    a = sub.add_parser("act", help="Care, play, tease or make up")
    a.add_argument("action", choices=ACTIONS)
    a.add_argument("detail", nargs="*", default=[])
    a.add_argument("--event-id")
    sub.add_parser("remember", help="Save a memory").add_argument("text")
    sub.add_parser("forget", help="Remove one saved memory").add_argument("id")
    sub.add_parser("config", help="Print hook configuration without installing it").add_argument("host", choices=["codex", "claude"])
    chat = sub.add_parser("chat", help="Chat using an installed AI CLI")
    chat.add_argument("--backend", choices=["codex", "claude"], required=True)
    chat.add_argument("--message", help="Send one message and exit")
    return p


def render(value):
    if value is None:
        return "No character yet. Start with sai create --help."
    if isinstance(value, dict) and "context" in value:
        return value["context"]
    if isinstance(value, dict) and value.get("kind") == "scripted-demo":
        lines = ["SAI · SCRIPTED DEMO / sample dialogue, real state changes", value["note"], ""]
        for row in value["events"]:
            lines += [f"> {row['action']} {row['detail']}", f"Ari [{MOOD_NAMES[row['mood']]}]: {row['line']}", ""]
        return "\n".join(lines)
    if isinstance(value, dict) and "reason" in value:
        return ("Applied" if value["accepted"] else "Declined") + " · " + value["reason"] + "\n" + render(value["state"])
    if isinstance(value, dict) and "needs" in value:
        mode = "ON" if value.get("enabled", True) else "OFF"
        lines = [f"{value['name']} · {ROLE_NAMES[value['role']]} · {mode} · {value['id']}",
                 f"Mood: {MOOD_NAMES[value['mood']]} / Affection {value['affection']} / Trust {value['trust']}",
                 "Needs (higher means more care needed): " + " / ".join(f"{key} {n:.0f}" for key, n in value["needs"].items()),
                 f"Shared experience: {value['xp']} · {value['stage']}"]
        if value["concern"]:
            lines.append("Still on their mind: " + value["concern"])
        return "\n".join(lines)
    if isinstance(value, list):
        return "\n\n".join(render(v) for v in value) or "Nothing here yet."
    return json.dumps(value, ensure_ascii=False, indent=2)


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    args = parser().parse_args(argv)
    store = Store(args.home)
    try:
        cmd = args.command
        if cmd == "create":
            value = store.create(args.name, args.role, args.temperament, likes=args.like,
                                 dislikes=args.dislike, boundaries=args.boundary, backstory=args.backstory)
        elif cmd in ("status", "list", "off", "memories"):
            value = getattr(store, cmd)()
        elif cmd == "use":
            value = store.use(args.id)
        elif cmd == "act":
            value = store.act(args.action, " ".join(args.detail), event_id=args.event_id)
        elif cmd == "remember":
            value = store.remember(args.text)
        elif cmd == "forget":
            store.forget(args.id)
            value = {"forgotten": args.id}
        elif cmd == "context":
            snapshot = store.snapshot()
            value = {"context": build_context(snapshot["state"], snapshot["memories"], store.home)}
        elif cmd == "demo":
            value = demo()
        elif cmd == "config":
            value = hook_config(args.host)
        elif cmd == "hook":
            try:
                payload = json.loads(sys.stdin.buffer.read(400001).decode("utf-8"))
                value = handle_hook(payload, store)
            except (ValueError, OSError):
                value = {"systemMessage": "SAI: invalid hook input; persona unchanged."}
            print(json.dumps(value, ensure_ascii=False))
            return 0
        elif cmd == "chat":
            from .chat import run_chat
            return run_chat(store, args.backend, args.message, args.json)
        print(json.dumps(value, ensure_ascii=False) if args.json or cmd == "config" else render(value))
        return 0
    except (ValueError, OSError, RuntimeError) as exc:
        message = str(exc)
        print(json.dumps({"error": message}, ensure_ascii=False) if args.json else "SAI: " + message, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
