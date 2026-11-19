"""Check English runtime strings and local links in the public entry documents."""
import json
from pathlib import Path
import re


def main():
    root = Path(__file__).resolve().parents[1]
    files = ["README.md", "README.en.md", "README.ko.md", "docs/INTEGRATION.md",
             "docs/INTEGRATION.ko.md", "docs/PILOT.md", "docs/verification/README.md"]
    errors = []
    for name in files:
        path = root / name
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append({"file": name, "broken_link": target})
    for path in (root / "sai").glob("*.py"):
        if re.search(r"[\uac00-\ud7a3]", path.read_text(encoding="utf-8")):
            errors.append({"file": path.name, "error": "Korean literal remains in runtime source"})
    report = {"status": "FAIL" if errors else "PASS", "checks": ["runtime source uses English text",
              "local links in both READMEs, integration guides, pilot and verification index resolve"], "errors": errors}
    (root / "docs/verification/english-0.1.1.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report))
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
