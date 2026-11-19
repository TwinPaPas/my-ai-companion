"""Inspect distributable source paths/content without printing potential secrets."""
import json
from pathlib import Path
import re
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=root).decode().split("\0")
    patterns = [re.compile(r"sk-[A-Za-z0-9_-]{25,}"), re.compile(r"gh[pousr]_[A-Za-z0-9]{25,}"),
                re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
                re.compile(r"C:[/\\]Users[/\\][^/\\\s]+", re.IGNORECASE)]
    problems = []
    count = 0
    for name in sorted(set(names) - {""}):
        path = root / name
        if not path.is_file():
            continue
        count += 1
        if path.suffix in (".db", ".sqlite", ".pem", ".key", ".pyc") or path.name == ".env":
            problems.append({"file": name, "reason": "private/runtime artifact"})
            continue
        try:
            content = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            problems.append({"file": name, "reason": "unexpected binary"})
            continue
        if any(pattern.search(content) for pattern in patterns):
            problems.append({"file": name, "reason": "possible credential or personal machine path; inspect locally"})
    result = {"status": "FAIL" if problems else "PASS", "files_checked": count,
              "scope": "heuristic check of tracked/unignored source; not a guarantee of absence of secrets", "findings": problems}
    destination = root / "docs" / "verification" / "release-check.json"
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))
    return bool(problems)


if __name__ == "__main__":
    sys.exit(main())
