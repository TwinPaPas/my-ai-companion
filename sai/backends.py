"""Use installed, authenticated CLIs; never evaluate dialogue as shell code."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess


def resolve_executable(host):
    configured = os.environ.get(f"SAI_{host.upper()}_BIN")
    found = configured or shutil.which(host)
    if not found:
        raise RuntimeError(f"{host} CLI not found. Install/login first, or set SAI_{host.upper()}_BIN.")
    path = Path(found)
    if os.name == "nt" and path.suffix.lower() in (".cmd", ".bat"):
        # Official npm Claude shim points at this native executable. Do not run
        # a batch shell with interpolated text or rewrite the user's launcher.
        native = path.parent / "node_modules" / "@anthropic-ai" / "claude-code" / "bin" / "claude.exe"
        if host == "claude" and native.is_file():
            return str(native)
        raise RuntimeError(f"Set SAI_{host.upper()}_BIN to a native executable (batch launchers are not evaluated).")
    if not path.is_file():
        raise RuntimeError(f"Configured {host} executable does not exist")
    return str(path)


def build_command(host, executable=None):
    if host not in ("codex", "claude"):
        raise ValueError("Unknown backend")
    executable = executable or resolve_executable(host)
    if host == "codex":
        return [executable, "--no-daemon", "exec", "--ephemeral", "--skip-git-repo-check",
                "--sandbox", "read-only", "--json", "-"]
    return [executable, "--print", "--output-format", "json", "--no-session-persistence", "--tools", ""]


def run_command(command, prompt, timeout=120):
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    try:
        completed = subprocess.run(command, input=prompt, capture_output=True, text=True,
                                   encoding="utf-8", errors="replace", timeout=timeout,
                                   shell=False, creationflags=flags)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Model CLI timed out after {timeout}s; no reply was saved") from exc
    except OSError as exc:
        raise RuntimeError("Could not start the model CLI: " + str(exc)) from exc
    if completed.returncode:
        # Keep auth tokens and incidental host diagnostic output out of replies.
        raise RuntimeError(f"Model CLI failed (exit {completed.returncode}). Check its login, permissions and connection directly. No simulated reply was substituted.")
    return completed.stdout


def extract_reply(host, output):
    replies = []
    for line in output.splitlines():
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(record, dict):
            continue
        if host == "claude":
            if record.get("is_error"):
                raise RuntimeError("Claude returned an error; no reply was saved")
            if isinstance(record.get("result"), str):
                replies.append(record["result"])
        else:
            if record.get("type") == "turn.failed":
                raise RuntimeError("Codex turn failed; no reply was saved")
            item = record.get("item", {})
            if record.get("type") == "item.completed" and item.get("type") == "agent_message":
                if isinstance(item.get("text"), str):
                    replies.append(item["text"])
    if not replies or not replies[-1].strip():
        raise RuntimeError(f"{host} returned no usable final reply; no simulated reply was substituted")
    return replies[-1].strip()


class CLIBackend:
    def __init__(self, host, timeout=120):
        self.host, self.timeout = host, timeout

    def generate(self, prompt):
        return extract_reply(self.host, run_command(build_command(self.host), prompt, self.timeout))
