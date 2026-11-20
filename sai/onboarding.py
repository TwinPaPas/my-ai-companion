"""A guided first conversation using the existing store and standalone chat."""
from . import backends
from .chat import run_chat
from .engine import checked_text


def choose(prompt, options, default):
    while True:
        answer = input(f"{prompt} [{default}]: ").strip().lower() or default
        if answer in options:
            return answer
        print("Choose " + ", ".join(options) + ".")


def ask_text(prompt, label, limit, required=False):
    while True:
        try:
            return checked_text(input(prompt + ": "), label, limit, not required)
        except ValueError as exc:
            print(str(exc))


def start(store, backend=None):
    try:
        if backend:
            backends.resolve_executable(backend)
        else:
            available, errors = [], []
            for host in ("claude", "codex"):
                try:
                    backends.resolve_executable(host)
                    available.append(host)
                except RuntimeError as exc:
                    errors.append(str(exc))
            if not available:
                raise RuntimeError("No supported CLI is available. " + " ".join(errors)
                                   + " Install and sign in to Claude Code or Codex, then run sai start again."
                                   + " You can try sai demo without a model.")
            if len(available) == 1:
                backend = available[0]
            else:
                print("Choose your existing AI CLI: 1) claude  2) codex")
                backend = available[int(choose("CLI", ("1", "2"), "1")) - 1]
        print(f"Found {backend}. Login and connection will be checked by your first live reply.")
        print("Standalone chat uses your provider's quota. Your existing CLI settings stay as they are.")
        characters = store.list()
        selected = None
        if characters:
            current = store.status()
            default = "1"
            print("Pick up your story. Choosing a saved character turns SAI ON and keeps their memories.")
            for i, character in enumerate(characters, 1):
                active = current and character["id"] == current["id"]
                if active:
                    default = str(i)
                marker = " (selected)" if active else ""
                print(f"{i}) {character['name']} / {character['role']}{marker}")
            print("n) Meet someone new")
            answer = choose("Character", tuple(str(i) for i in range(1, len(characters) + 1)) + ("n",), default)
            if answer != "n":
                selected = characters[int(answer) - 1]
        if selected is None:
            print("Let's meet your fictional adult companion. Ctrl+C cancels before saving.")
            name = ask_text("Their name", "name", 60, required=True)
            print("1) Sweetheart  2) Girl best friend  3) Guy best friend  4) Custom")
            role = ("lover", "female-friend", "male-friend", "custom")[int(choose("Relationship", ("1", "2", "3", "4"), "2")) - 1]
            backstory = ask_text("Your shared background", "backstory", 1000, required=True) if role == "custom" else ""
            print("1) Playful  2) Warm  3) Blunt (independent of relationship)")
            temperament = ("playful", "warm", "blunt")[int(choose("Temperament", ("1", "2", "3"), "1")) - 1]
            like = ask_text("Something they like (optional)", "like", 100)
            dislike = ask_text("Something they dislike (optional)", "dislike", 100)
            selected = store.create(name, role, temperament, likes=[like] if like else [],
                                    dislikes=[dislike] if dislike else [], backstory=backstory)
        else:
            selected = store.use(selected["id"])
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled. Your saved characters are unchanged.")
        return 0
    print(f"You're ready to talk with {selected['name']}. Say hello or tell them about your day.")
    print("Keep something for later: /sai remember TEXT. /quit leaves chat; /sai off turns the mode off.")
    return run_chat(store, backend)
