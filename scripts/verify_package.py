"""Install a built wheel into a temporary venv and exercise it outside the checkout."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import venv


def main():
    root = Path(__file__).resolve().parents[1]
    wheel = root / "dist" / "sai_companion-0.1.0-py3-none-any.whl"
    report = {"python": platform.python_version(), "platform": platform.system(), "status": "RUNNING", "checks": []}
    try:
        report["wheel_sha256"] = hashlib.sha256(wheel.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory(prefix="sai-package-") as folder:
            base = Path(folder).resolve()
            environment = base / "venv"
            venv.EnvBuilder(with_pip=True).create(environment)
            python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
            kwargs = dict(cwd=base, capture_output=True, text=True, encoding="utf-8", timeout=60,
                          creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0)
            install = subprocess.run([str(python), "-m", "pip", "install", "--no-deps", str(wheel)], **kwargs)
            if install.returncode:
                raise RuntimeError("wheel install failed")
            def run(*args):
                r = subprocess.run([str(python), "-m", "sai", "--home", str(base / "state"), "--json", *args], **kwargs)
                if r.returncode:
                    raise RuntimeError("installed CLI failed: " + r.stderr[-500:])
                return json.loads(r.stdout)
            assert run("demo")["kind"] == "scripted-demo"
            for role in ["lover", "female-friend", "male-friend"]:
                created = run("create", "하루", "--role", role)
                assert run("status")["id"] == created["id"]
            assert len(run("list")) == 3
            run("act", "water")
            run("off")
            assert run("status")["enabled"] is False
            assert "SAI_MODE=OFF" in run("context")["context"]
            report["checks"] = ["wheel installed without runtime dependencies", "CLI works outside source checkout",
                                "three central roles created", "new process restored selected state", "off persists", "demo runs"]
            report["status"] = "PASS"
    except Exception as exc:
        report["status"] = "FAIL"
        report["error"] = str(exc)
    dest = root / "docs" / "verification" / "package.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
