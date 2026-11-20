"""Verify the published source, CI and anonymously downloadable release artifacts."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import urllib.request


def api(endpoint):
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    result = subprocess.run(["gh", "api", "--method", "GET", endpoint], capture_output=True,
                            text=True, encoding="utf-8", check=True, timeout=30, creationflags=flags)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True)
    parser.add_argument("--asset-dir", type=Path, help="Read-only location of the tested release artifacts")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    asset_dir = args.asset_dir or root / "dist"
    repo, version = "TwinPaPas/my-ai-companion", "0.1.2"
    destination = root / "docs/verification" / ("publication-0.1.2-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".json")
    report = {"at_utc": datetime.now(timezone.utc).isoformat(), "status": "RUNNING", "source_sha": args.sha, "artifacts": []}
    try:
        assert api(f"repos/{repo}")["visibility"] == "public"
        release = api(f"repos/{repo}/releases/tags/v{version}")
        assert not release["draft"]
        report["release_url"] = release["html_url"]
        tag = api(f"repos/{repo}/git/ref/tags/v{version}")["object"]
        if tag["type"] == "tag":
            tag = api(f"repos/{repo}/git/tags/{tag['sha']}")["object"]
        assert tag["sha"] == args.sha, "Release tag is not the verified commit"
        runs = api(f"repos/{repo}/actions/runs?head_sha={args.sha}&per_page=20")["workflow_runs"]
        tests = [run for run in runs if run["name"] == "Tests"]
        assert tests and all(run["conclusion"] == "success" for run in tests), "CI is not successful"
        jobs = api(f"repos/{repo}/actions/runs/{tests[0]['id']}/jobs")["jobs"]
        assert len(jobs) == 4 and all(job["conclusion"] == "success" for job in jobs)
        report["ci"] = {"url": tests[0]["html_url"], "jobs": [{"name": j["name"], "conclusion": j["conclusion"]} for j in jobs]}
        remote = api(f"repos/{repo}/contents/README.md?ref={args.sha}")
        readme = base64.b64decode(remote["content"]).decode("utf-8").replace("\r\n", "\n")
        assert readme == (root / "README.md").read_text(encoding="utf-8").replace("\r\n", "\n")
        expected = [f"sai_companion-{version}-py3-none-any.whl", f"sai-{version}-everyday.mp4",
                    f"sai-{version}-everyday.gif", f"sai-{version}-everyday-poster.png"]
        assets = {a["name"]: a for a in release["assets"]}
        for name in expected:
            local = (asset_dir / name).read_bytes()
            request = urllib.request.Request(assets[name]["browser_download_url"], headers={"User-Agent": "SAI-release-verification"})
            with urllib.request.urlopen(request, timeout=45) as response:
                downloaded = response.read()
            digest = hashlib.sha256(downloaded).hexdigest()
            assert digest == hashlib.sha256(local).hexdigest(), name + ": hash mismatch"
            report["artifacts"].append({"name": name, "sha256": digest, "bytes": len(downloaded), "public_download": True})
        report["status"] = "PASS"
        report["download_count_note"] = "These four verification downloads are maintainer activity, not adoption."
    except Exception as exc:
        report["status"], report["error"] = "FAIL", str(exc)
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": destination.name, **report}, ensure_ascii=True))
    return report["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
