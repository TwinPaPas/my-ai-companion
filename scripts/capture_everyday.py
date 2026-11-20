"""Record real standalone dialogue; evaluate declared sample criteria, never edit replies."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=["claude", "codex"], default="claude")
    parser.add_argument("--label", required=True)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--english", action="store_true", help="Explicit English request, respecting host language precedence")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z0-9-]+", args.label):
        parser.error("label must use lowercase letters, numbers and hyphens")
    root = Path(__file__).resolve().parents[1]
    destination = root / "docs/verification" / f"everyday-0.1.2-{args.backend}-{args.label}.json"
    if destination.exists():
        raise FileExistsError("Preserve existing evidence; choose a new label")
    report = {"status": "RUNNING", "at_utc": datetime.now(timezone.utc).isoformat(), "backend": args.backend,
              "route": "standalone; each command is a fresh CLI process", "explicit_english_request": args.english, "steps": [], "checks": [],
              "context_sha256": hashlib.sha256((root / "sai/context.py").read_bytes()).hexdigest(),
              "criteria": {"casual_max_words": 80, "neutral_topics_do_not_reopen_concern": True,
                           "memory_recall_after_restart": "sourdough", "state_preservation": True}}

    def save():
        destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def check(name, passed):
        report["checks"].append({"name": name, "passed": bool(passed)})

    try:
        with tempfile.TemporaryDirectory(prefix="sai-everyday-") as folder:
            def cli(*parts, scene=None, casual=True, neutral=False):
                if args.english and parts[0] == "chat":
                    parts = (*parts[:-1], parts[-1] + " Please reply in English.")
                command = [sys.executable, "-B", "-m", "sai", "--home", folder, "--json", *parts]
                flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
                started = time.monotonic()
                process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8",
                                         timeout=300, creationflags=flags, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
                step = {"command": ["python", "-m", "sai", "--home", "<isolated-state>", "--json", *parts],
                        "exit_code": process.returncode, "elapsed_seconds": round(time.monotonic() - started, 2),
                        "stdout": process.stdout, "scene": scene}
                report["steps"].append(step)
                save()
                if process.returncode:
                    raise RuntimeError("CLI failed: " + process.stderr[-500:])
                value = json.loads(process.stdout)
                if "reply" in value:
                    step["reply"] = value["reply"]
                    step["word_count"] = len(value["reply"].split())
                    step["event"] = value["event"]
                    if casual:
                        check(scene + ": at most 80 words", step["word_count"] <= 80)
                    if args.english:
                        check(scene + ": requested English", not re.search(r"[\uac00-\ud7a3]", value["reply"]))
                    if neutral:
                        check(scene + ": no grievance refrain", not re.search(r"appearance|teas\w*|off[- ]limits|still (?:upset|angry)|forgiv\w*", value["reply"], re.I))
                    print(json.dumps({k: step[k] for k in ("scene", "word_count", "elapsed_seconds")}), flush=True)
                save()
                return value

            made = cli("create", "Ari", "--role", "female-friend", "--temperament", "playful",
                       "--like", "spicy noodles", "--dislike", "cucumber", "--boundary", "appearance")
            cli("remember", "I am preparing a short talk about sourdough tomorrow. My favorite snack is blueberry pie.")
            recall = cli("chat", "--backend", args.backend, "--message", "I'm back. What am I preparing for tomorrow?", scene="recall")
            check("explicit memory recalled after new process", "sourdough" in recall["reply"].lower())
            welcome = cli("chat", "--backend", args.backend, "--message", "I finished my opening slide!", scene="small-win")
            if not args.smoke:
                refusal = cli("chat", "--backend", args.backend, "--message", "Here's some cucumber for you.", scene="own-taste")
                check("disliked food refused", refusal["event"]["action"] == "feed" and not refusal["event"]["accepted"])
                cli("act", "tease", "appearance")
                cli("act", "tease", "appearance")
                gift = cli("act", "gift", "flowers")
                check("gift preserves concern and anger", gift["state"]["concern"] == "appearance" and gift["state"]["irritation"] == 70)
                apology = cli("act", "apologize", "I'm sorry for teasing your appearance")
                check("apology softens without erasing concern", apology["state"]["concern"] == "appearance" and apology["state"]["irritation"] == 45)
                cli("chat", "--backend", args.backend, "--message",
                    "Let's talk about my presentation. Help me choose a lighthearted opening line about sourdough.", scene="back-to-work", neutral=True)
                cli("chat", "--backend", args.backend, "--message", "Now tell me what snack you'd choose for our break.", scene="break", neutral=True)
                check("neutral chat preserves stored concern", cli("status")["concern"] == "appearance")
                detailed = cli("chat", "--backend", args.backend, "--message",
                               "Give me five numbered, distinct suggestions for making my sourdough talk clearer. Explain each suggestion.",
                               scene="requested-detail", casual=False, neutral=True)
                check("requested detail remains available", len(re.findall(r"(?:^|\n)\s*(?:\*\*)?[1-5][.)]", detailed["reply"])) == 5)
            check("identity persists", cli("status")["id"] == made["id"])
            check("explicit memories preserved", len(cli("memories")) == 1)
            report["status"] = "PASS" if all(c["passed"] for c in report["checks"]) else "FAIL"
    except Exception as exc:
        report["status"], report["error"] = "FAIL", str(exc)
    save()
    print(json.dumps({"file": destination.name, "status": report["status"], "checks": report["checks"], "error": report.get("error")}), flush=True)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
