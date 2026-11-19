"""Capture real Claude dialogue and persistence across separate CLI processes.

Uses the existing provider quota. Replies are never replaced by scripted text.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / "docs/verification/showcase-0.1.1.json"
    report = {"status": "RUNNING", "at_utc": datetime.now(timezone.utc).isoformat(),
              "backend": "claude", "presentation": "Edited playback of real stdout, not a real-time screen capture",
              "steps": [], "checks": []}
    try:
        with tempfile.TemporaryDirectory(prefix="sai-showcase-") as folder:
            def cli(*args):
                command = [sys.executable, "-B", "-m", "sai", "--home", folder, "--json", *args]
                flags = subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS if os.name == "nt" else 0
                process = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8",
                                         timeout=300, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"), creationflags=flags)
                step = {"command": ["python", "-m", "sai", "--home", "<isolated-demo-state>", "--json", *args],
                        "exit_code": process.returncode, "stdout": process.stdout}
                report["steps"].append(step)
                if process.returncode:
                    raise RuntimeError("CLI process failed: " + process.stderr[-800:])
                value = json.loads(process.stdout)
                if isinstance(value, dict) and "reply" in value:
                    step["reply"] = value["reply"]
                    step["mood"] = value["event"]["state"]["mood"]
                    step["concern"] = value["event"]["state"]["concern"]
                    step["irritation"] = value["event"]["state"]["irritation"]
                    print(json.dumps({k: step[k] for k in ("reply", "mood", "concern")}), flush=True)
                return value

            created = cli("create", "Ari", "--role", "female-friend", "--temperament", "playful",
                          "--like", "spicy noodles", "--dislike", "cucumber", "--boundary", "appearance",
                          "--backstory", "An adult fictional friend who speaks English, keeps replies to one short sentence, and has her own tastes.")
            cli("act", "tease", "appearance")
            conflict = cli("chat", "--backend", "claude", "--message", "/sai act tease appearance")
            reopened = cli("status")
            assert reopened["id"] == created["id"]
            assert reopened["concern"] == "appearance" and reopened["mood"] == "angry"
            assert reopened["irritation"] == conflict["event"]["state"]["irritation"]
            recall = cli("chat", "--backend", "claude", "--message",
                         "You still seem upset. What happened earlier? Answer in English in one short sentence.")
            assert recall["event"]["action"] == "talk"
            assert any(word in recall["reply"].lower() for word in ("appearance", "looks", "look", "teas", "jok")), "reply did not recall the conflict"
            gift = cli("chat", "--backend", "claude", "--message", "/sai act gift flowers")
            assert gift["event"]["state"]["concern"] == "appearance"
            assert gift["event"]["state"]["mood"] == "angry"
            apology = cli("chat", "--backend", "claude", "--message",
                          "/sai act apologize I'm sorry for teasing your appearance")
            assert apology["event"]["state"]["mood"] == "sulking"
            assert apology["event"]["state"]["irritation"] < gift["event"]["state"]["irritation"]
            for value in (conflict, recall, gift, apology):
                assert not any("\uac00" <= c <= "\ud7a3" for c in value["reply"]), "requested English dialogue was not returned"
            report["checks"] = ["all CLI commands returned exit 0", "each CLI call was a fresh process",
                                "identity and unresolved conflict survived chat process exit",
                                "real generated reply recalled the conflict after restart",
                                "flowers did not erase anger or concern", "apology reduced irritation without instant forgiveness",
                                "English replies observed; no scripted replacement"]
            report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "checks": report["checks"], "error": report.get("error")}))
    return report["status"] != "PASS"


if __name__ == "__main__":
    sys.exit(main())
