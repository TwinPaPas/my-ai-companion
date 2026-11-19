import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "sai", "--home", self.tmp.name,
                               "--json", *args], capture_output=True, text=True,
                              encoding="utf-8", env=dict(os.environ, PYTHONUTF8="1"), timeout=10)

    def test_real_process_roundtrip_and_off(self):
        created = self.run_cli("create", "하루", "--role", "male-friend", "--dislike", "오이")
        self.assertEqual(created.returncode, 0, created.stderr)
        char = json.loads(created.stdout)
        state = json.loads(self.run_cli("status").stdout)
        self.assertEqual(state["id"], char["id"])
        refusal = json.loads(self.run_cli("act", "feed", "오이").stdout)
        self.assertFalse(refusal["accepted"])
        self.assertEqual(self.run_cli("off").returncode, 0)
        self.assertFalse(json.loads(self.run_cli("status").stdout)["enabled"])
        self.assertNotEqual(self.run_cli("act", "water").returncode, 0)
        self.assertEqual(self.run_cli("use", char["id"]).returncode, 0)

    def test_context_before_creation_is_empty_without_database(self):
        r = self.run_cli("context")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["context"], "")
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())

    def test_metacharacters_are_data(self):
        self.run_cli("create", "민수", "--role", "lover")
        payload = '$(whoami); `echo secret` & | < >'
        r = self.run_cli("remember", payload)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["text"], payload)

    def test_invalid_action_does_not_change_state(self):
        self.assertEqual(self.run_cli("create", "민수", "--role", "lover").returncode, 0)
        before = self.run_cli("status").stdout
        self.assertNotEqual(self.run_cli("act", "erase").returncode, 0)
        self.assertEqual(self.run_cli("status").stdout, before)

    def test_demo_is_scripted_and_does_not_create_user_state(self):
        r = self.run_cli("demo")
        self.assertEqual(r.returncode, 0, r.stderr)
        result = json.loads(r.stdout)
        self.assertEqual(result["kind"], "scripted-demo")
        self.assertIn("angry", [row["mood"] for row in result["events"]])
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())


if __name__ == "__main__":
    unittest.main()
