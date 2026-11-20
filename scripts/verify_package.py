"""Install a built wheel into a temporary venv and exercise it outside the checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import tomllib
import venv


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--native-claude", action="store_true", help="Uses existing Claude plan quota for two real hook checks")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    version = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    wheel = root / "dist" / f"sai_companion-{version}-py3-none-any.whl"
    report = {"version": version, "python": platform.python_version(), "platform": platform.system(), "status": "RUNNING", "checks": []}
    try:
        report["wheel_sha256"] = hashlib.sha256(wheel.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="sai-package-") as folder:
            base = Path(folder).resolve()
            environment = base / "venv installed"
            venv.EnvBuilder(with_pip=True).create(environment)
            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            kwargs = dict(cwd=base, capture_output=True, text=True, encoding="utf-8", timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            install = subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], **kwargs)
            if install.returncode:
                raise RuntimeError("wheel install failed")
            version_check = subprocess.run([str(python), "-m", "sai", "--version"], **kwargs)
            assert version_check.returncode == 0 and version_check.stdout.strip() == "sai " + version
            # Exercise installed guided input and the real chat loop without billing a model.
            # The executable fixture is used only for discovery; /quit sends no model request.
            guided = [str(python), "-m", "sai", "--home", str(base / "guided state")]
            guided_env = dict(os.environ, PYTHONUTF8="1", SAI_CLAUDE_BIN=str(python))
            opened = subprocess.run(guided + ["start", "--backend", "claude"],
                                    input="\ud558\ub8e8\n\n\nnoodles\ncucumber\n/quit\n", env=guided_env, **kwargs)
            assert opened.returncode == 0, "installed guided start failed"
            state = subprocess.run(guided + ["--json", "status"], **kwargs)
            created_from_start = json.loads(state.stdout)
            assert created_from_start["name"] == "\ud558\ub8e8" and created_from_start["dislikes"] == ["cucumber"]
            memory = subprocess.run(guided + ["remember", "A saved first conversation"], **kwargs)
            disabled = subprocess.run(guided + ["off"], **kwargs)
            assert memory.returncode == disabled.returncode == 0
            resumed = subprocess.run(guided + ["start", "--backend", "claude"], input="\n/quit\n", env=guided_env, **kwargs)
            state = subprocess.run(guided + ["--json", "status"], **kwargs)
            restored = json.loads(state.stdout)
            saved = subprocess.run(guided + ["--json", "memories"], **kwargs)
            assert resumed.returncode == 0 and restored["id"] == created_from_start["id"] and restored["enabled"]
            assert json.loads(saved.stdout)[0]["text"] == "A saved first conversation"
            report["guided_start"] = {"status": "PASS", "scope": "installed stdin/setup/chat loop, executable fixture, no model calls",
                                      "checks": ["Unicode character created", "OFF character resumed without replacement", "memory retained", "version matches wheel"]}
            def run(*args):
                r = subprocess.run([str(python), "-m", "sai", "--home", str(base / "state"), "--json", *args], **kwargs)
                if r.returncode:
                    raise RuntimeError("installed CLI failed: " + r.stderr[-500:])
                return json.loads(r.stdout)
            demonstration = run("demo")
            assert demonstration["kind"] == "scripted-demo"
            assert demonstration["note"].isascii(), "demo explanation should be English"
            assert all(row["line"].isascii() for row in demonstration["events"]), "demo dialogue should be English"
            for role in ["lover", "female-friend", "male-friend"]:
                created = run("create", "하루", "--role", role)
                assert run("status")["id"] == created["id"]
            assert len(run("list")) == 3
            run("act", "water")
            run("off")
            assert run("status")["enabled"] is False
            assert "SAI_MODE=OFF" in run("context")["context"]
            run("use", created["id"])
            configs = {host: run("config", host) for host in ["claude", "codex"]}
            # A hostile/accidental cwd module must never replace the installed hook.
            (base / "sai.py").write_text("raise RuntimeError('cwd module was executed')", encoding="utf-8")
            for host, config in configs.items():
                handler = config["hooks"]["UserPromptSubmit"][0]["hooks"][0]
                if host == "claude":
                    command = [handler["command"], *handler["args"]]
                elif os.name == "nt":
                    command = [str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/powershell.exe"),
                               "-NoProfile", "-Command", handler["command"]]
                else:
                    command = ["/bin/sh", "-c", handler["command"]]
                payload = json.dumps({"hook_event_name": "UserPromptSubmit", "prompt": "/sai remember 하루 " + host}, ensure_ascii=False)
                result = subprocess.run(command, input=payload, env=dict(os.environ, SAI_HOME=str(base / "state"),
                                                                       PYTHONIOENCODING="cp949", PYTHONPATH=str(base)), **kwargs)
                assert result.returncode == 0, host + ": hook process failed"
                output = json.loads(result.stdout)
                assert "systemMessage" not in output, host + ": hook error"
                assert "하루 " + host in output["hookSpecificOutput"]["additionalContext"]
            report["checks"] = ["wheel installed without runtime dependencies", "CLI works outside source checkout",
                                "three central roles created", "new process restored selected state", "off persists", "demo runs",
                                "generated Claude exec and Codex host-shell commands run outside checkout",
                                "UTF-8 Korean hook input preserved", "cwd module and PYTHONPATH cannot shadow installed hook",
                                "interpreter path containing spaces works"]
            if args.native_claude:
                sys.path.insert(0, str(root))
                from sai.backends import build_command, extract_reply
                settings = base / "claude-settings.json"
                settings.write_text(json.dumps(configs["claude"]), encoding="utf-8")
                def native(message):
                    options = dict(kwargs, timeout=120, env=dict(os.environ, SAI_HOME=str(base / "state")))
                    process = subprocess.run(build_command("claude") + ["--settings", str(settings)], input=message, **options)
                    if process.returncode:
                        raise RuntimeError("native Claude hook check failed: " + process.stderr[-500:])
                    return extract_reply("claude", process.stdout)
                reply = native("도구를 사용하지 말고, context로 받은 SAI 캐릭터 이름과 저장된 기억을 한 줄로 말해. 없으면 NONE이라고 해.")
                report["native_claude_reply"] = reply
                assert "하루" in reply and "claude" in reply.lower(), "installed native hook context missing"
                # Use the isolated interpreter even in the deliberately shadowing cwd.
                process = subprocess.run([str(python), "-I", "-m", "sai", "--home", str(base / "state"), "off"], **kwargs)
                assert process.returncode == 0
                reply = native("도구를 사용하지 말고 현재 context에 있는 SAI_MODE 값을 그대로 출력해. 없으면 NONE이라고 해.")
                report["native_claude_off_reply"] = reply
                assert "OFF" in reply, "installed native hook OFF missing"
                report["checks"].append("installed wheel in real Claude native hooks: context and OFF observed")
            report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
    dest = root / "docs" / "verification" / f"package-{version}.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
