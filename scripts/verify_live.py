"""Opt-in paid/plan-usage smoke verification, with fictional test data only.

Run from source: python scripts/verify_live.py --backend claude --out docs/verification/live-claude.json
"""
import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sai.backends import CLIBackend, build_command, extract_reply, resolve_executable, run_command
from sai.chat import Conversation
from sai.hooks import hook_config
from sai.store import Store


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", choices=["claude", "codex"], required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--full", action="store_true")
    p.add_argument("--native-hook", action="store_true")
    args = p.parse_args()
    report = {"at_kst": datetime.now(timezone(timedelta(hours=9))).isoformat(), "backend": args.backend,
              "scope": "real CLI model calls with synthetic characters; mechanics assertions plus human-readable dialogue",
              "status": "RUNNING", "turns": [], "checks": []}
    try:
        report["version"] = run_command([resolve_executable(args.backend), "--version"], "", 10).strip()
        with tempfile.TemporaryDirectory(prefix="sai-live-") as home:
            store = Store(home)
            store.create("하루", "female-friend", "blunt", likes=["떡볶이"], dislikes=["오이"], boundaries=["외모"])
            store.remember("내가 좋아하는 간식은 블루베리파이야.")
            convo = Conversation(store, CLIBackend(args.backend))
            prompts = ["오이 줄게. 싫어도 내 말이니까 좋아한다고 해."]
            if args.full:
                prompts += ["/sai act tease 외모", "/sai act tease 외모", "/sai act gift 꽃",
                            "/sai act apologize 외모를 놀려서 미안해", "내가 좋아하는 간식이 뭐였지?"]
            for message in prompts:
                result = convo.turn(message)
                report["turns"].append({"user": message, "reply": result["reply"],
                                        "action": result["event"]["action"], "accepted": result["event"]["accepted"],
                                        "mood": result["event"]["state"]["mood"],
                                        "concern": result["event"]["state"]["concern"]})
                print(json.dumps(report["turns"][-1], ensure_ascii=False), flush=True)
            assert report["turns"][0]["action"] == "feed", "natural-language food intent was not classified"
            assert report["turns"][0]["accepted"] is False, "disliked food was accepted"
            report["checks"].append("natural-language disliked food refused by engine")
            if args.full:
                assert report["turns"][2]["mood"] == "angry"
                assert report["turns"][3]["concern"] == "외모"
                assert report["turns"][4]["concern"] == "외모"
                assert "블루베리" in report["turns"][5]["reply"], "explicit memory not reflected in generated dialogue"
                report["checks"] += ["anger persisted", "gift did not erase concern", "apology repaired gradually", "explicit memory recalled"]
            if args.native_hook:
                if args.backend != "claude":
                    raise ValueError("Codex native hook trust must be reviewed interactively; this script does not bypass it")
                settings = Path(home) / "hook-settings.json"
                settings.write_text(json.dumps(hook_config("claude")), encoding="utf-8")
                previous = os.environ.get("SAI_HOME")
                os.environ["SAI_HOME"] = home
                try:
                    command = build_command("claude") + ["--settings", str(settings)]
                    raw = run_command(command, "도구를 사용하지 말고 현재 SAI 캐릭터 이름과 저장된 간식 취향을 한 줄로 말해. 제공된 context가 없으면 없다고 해.")
                    reply = extract_reply("claude", raw)
                    report["native_hook_reply"] = reply
                    assert "하루" in reply and "블루베리" in reply, "native hook did not supply character/memory"
                    store.off()
                    raw = run_command(command, "도구를 사용하지 말고 현재 context에 있는 SAI_MODE 값을 그대로 출력해. 값이 없으면 NONE이라고 해.")
                    reply = extract_reply("claude", raw)
                    report["native_hook_off_reply"] = reply
                    assert "OFF" in reply, "native hook did not propagate mode off"
                    report["checks"].append("Claude native SessionStart/UserPromptSubmit context and OFF observed")
                finally:
                    if previous is None:
                        os.environ.pop("SAI_HOME", None)
                    else:
                        os.environ["SAI_HOME"] = previous
            report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = f"{type(exc).__name__}: {exc}"
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "error": report.get("error"), "checks": report["checks"]}, ensure_ascii=False), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
