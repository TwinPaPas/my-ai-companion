from __future__ import annotations

import argparse
import json
import sys

from .context import build_context
from .demo import demo
from .engine import ACTIONS, ROLES, TEMPERAMENTS
from .hooks import handle_hook, hook_config
from .store import Store

ROLE_NAMES = {"lover": "애인", "female-friend": "여사친", "male-friend": "남사친", "custom": "직접 설정"}
MOOD_NAMES = {"curious": "알아가는 중", "comfortable": "편안함", "sulking": "삐짐", "angry": "화남", "tired": "피곤함"}


def parser():
    p = argparse.ArgumentParser(prog="sai", description="사이 · 나만의 AI 키우기 — 관계, 돌봄, 자기 취향이 있는 캐릭터")
    p.add_argument("--home", help="별도 상태 폴더 (기본 ~/.sai 또는 SAI_HOME)")
    p.add_argument("--json", action="store_true", help="기계가 읽을 JSON 출력")
    p.add_argument("--version", action="version", version="sai 0.1.0")
    sub = p.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create", help="캐릭터 만들고 시작하기")
    c.add_argument("name")
    c.add_argument("--role", choices=ROLES, required=True)
    c.add_argument("--temperament", choices=TEMPERAMENTS, default="playful")
    for arg in ("like", "dislike", "boundary"):
        c.add_argument("--" + arg, action="append", default=[])
    c.add_argument("--backstory", default="")
    for command, help_text in [("list", "만든 캐릭터"), ("status", "현재 상태"), ("off", "모드 해제 (기억 보존)"),
                               ("context", "현재 캐릭터 context"), ("memories", "저장한 기억"), ("demo", "API 없는 돌봄 시연"),
                               ("hook", "AI CLI lifecycle hook")]:
        sub.add_parser(command, help=help_text)
    sub.add_parser("use", help="캐릭터 불러오기").add_argument("id")
    a = sub.add_parser("act", help="돌봄·장난·화해")
    a.add_argument("action", choices=ACTIONS)
    a.add_argument("detail", nargs="*", default=[])
    a.add_argument("--event-id")
    sub.add_parser("remember", help="기억 남기기").add_argument("text")
    sub.add_parser("forget", help="기억 한 항목 지우기").add_argument("id")
    sub.add_parser("config", help="hook 설정 출력 (자동 설치 안 함)").add_argument("host", choices=["codex", "claude"])
    chat = sub.add_parser("chat", help="설치된 AI CLI와 대화")
    chat.add_argument("--backend", choices=["codex", "claude"], required=True)
    chat.add_argument("--message", help="한 번만 말하고 종료")
    return p


def render(value):
    if value is None:
        return "아직 캐릭터가 없습니다. sai create --help 로 시작하세요."
    if isinstance(value, dict) and "context" in value:
        return value["context"]
    if isinstance(value, dict) and value.get("kind") == "scripted-demo":
        lines = ["SAI · SCRIPTED DEMO / 대사는 예시, 상태는 실제 계산", value["note"], ""]
        for row in value["events"]:
            lines += [f"> {row['action']} {row['detail']}", f"하루 [{MOOD_NAMES[row['mood']]}]: {row['line']}", ""]
        return "\n".join(lines)
    if isinstance(value, dict) and "reason" in value:
        return ("받아들임" if value["accepted"] else "거절") + " · " + value["reason"] + "\n" + render(value["state"])
    if isinstance(value, dict) and "needs" in value:
        mode = "ON" if value.get("enabled", True) else "OFF"
        lines = [f"{value['name']} · {ROLE_NAMES[value['role']]} · {mode} · {value['id']}",
                 f"기분: {MOOD_NAMES[value['mood']]} / 친밀감 {value['affection']} / 신뢰 {value['trust']}",
                 "필요 (높을수록 챙겨 주세요): " + " / ".join(f"{key} {n:.0f}" for key, n in value["needs"].items()),
                 f"함께 쌓은 경험: {value['xp']} · {value['stage']}"]
        if value["concern"]:
            lines.append("마음에 남은 일: " + value["concern"])
        return "\n".join(lines)
    if isinstance(value, list):
        return "\n\n".join(render(v) for v in value) or "없습니다."
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
            value = {"context": build_context(store.status(), store.memories())}
        elif cmd == "demo":
            value = demo()
        elif cmd == "config":
            value = hook_config(args.host)
        elif cmd == "hook":
            try:
                payload = json.loads(sys.stdin.read(200001))
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
