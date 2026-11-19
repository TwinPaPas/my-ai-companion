"""Behavioral regressions found by the independent release review."""
from contextlib import closing, redirect_stdout
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from sai.chat import Conversation, run_chat
from sai.cli import render
from sai.hooks import handle_hook, hook_config
from sai.store import Store


class ReviewRegressions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)
        self.a = self.store.create("A", "lover", boundaries=["hair"])

    def hook(self, prompt, turn="one"):
        return handle_hook(dict(hook_event_name="UserPromptSubmit", session_id="session",
                                turn_id=turn, prompt=prompt), self.store)

    def test_remember_retry_is_idempotent(self):
        self.hook("/sai remember jazz")
        self.hook("/sai remember jazz")
        self.assertEqual(len(self.store.memories()), 1)

    def test_old_off_and_use_do_not_override_new_selection(self):
        for command in ["/sai off", "/sai use " + self.a["id"]]:
            self.hook(command, command)
            b = self.store.create("B", "male-friend")
            self.hook(command, command)
            self.assertTrue(self.store.status()["enabled"])
            self.assertEqual(self.store.status()["id"], b["id"])

    def test_old_action_is_not_applied_to_new_character(self):
        self.hook("/sai act water")
        self.store.create("B", "male-friend")
        before = self.store.status()
        self.hook("/sai act water")
        self.assertEqual(self.store.status(), before)

    def test_command_free_text_is_not_shell_syntax(self):
        for i, text in enumerate([r"C:\music\jazz", "I'm learning jazz", 'say "hello" to me']):
            self.hook("/sai remember " + text, str(i))
        self.assertEqual([m["text"] for m in self.store.memories()],
                         [r"C:\music\jazz", "I'm learning jazz", 'say "hello" to me'])

    def test_off_context_survives_command_or_payload_error(self):
        self.store.off()
        for text in ["/sai act water", "x" * 100001]:
            result = self.hook(text)
            self.assertIn("SAI_MODE=OFF", result.get("hookSpecificOutput", {}).get("additionalContext", ""))

    def test_hook_reads_utf8_even_with_legacy_stdin_encoding(self):
        payload = json.dumps(dict(hook_event_name="UserPromptSubmit", prompt="/sai remember 하루"),
                             ensure_ascii=False).encode("utf-8")
        result = subprocess.run([sys.executable, "-m", "sai", "--home", self.tmp.name, "hook"],
                                input=payload, capture_output=True, timeout=10,
                                env=dict(os.environ, PYTHONUTF8="0", PYTHONIOENCODING="cp949"))
        self.assertEqual(result.returncode, 0)
        self.assertEqual([m["text"] for m in self.store.memories()], ["하루"])

    def test_memory_list_and_empty_off_print_without_model(self):
        for message in ["/sai memories", "/sai off"]:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(run_chat(self.store, "claude", message), 0)
        empty = Store(Path(self.tmp.name) / "empty")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(run_chat(empty, "claude", "/sai off"), 0)

    def test_list_reflects_off_and_inactive_characters(self):
        self.store.create("B", "male-friend")
        self.assertEqual([c["enabled"] for c in self.store.list()], [False, True])
        self.store.off()
        self.assertNotIn("ON", render(self.store.list()))

    def test_incomplete_version_one_schema_is_never_written(self):
        other = Store(Path(self.tmp.name) / "foreign")
        other.home.mkdir()
        with closing(sqlite3.connect(other.path)) as db:
            db.executescript("CREATE TABLE meta(key TEXT PRIMARY KEY,value TEXT NOT NULL);"
                             "CREATE TABLE characters(id TEXT PRIMARY KEY,state TEXT NOT NULL);"
                             "INSERT INTO meta VALUES('enabled','foreign'); PRAGMA user_version=1;")
        with self.assertRaisesRegex(ValueError, "schema"):
            other.off()
        with closing(sqlite3.connect(other.path)) as db:
            self.assertEqual(db.execute("SELECT value FROM meta").fetchone()[0], "foreign")

    def test_invented_intent_detail_cannot_change_emotion(self):
        class Model:
            def generate(self, prompt):
                return '{"action":"tease","detail":"hair"}'
        before = self.store.status()
        with self.assertRaises(ValueError):
            Conversation(self.store, Model()).turn("How is the weather?")
        self.assertEqual(self.store.status(), before)

    def test_switch_between_action_and_dialogue_never_crosses_history(self):
        original = self.store.act
        def switching(*args, **kwargs):
            result = original(*args, **kwargs)
            self.store.create("B", "male-friend")
            return result
        self.store.act = switching
        class Model:
            def generate(self, prompt):
                return "A's reply"
        with self.assertRaises(ValueError):
            Conversation(self.store, Model()).turn("/sai act water")
        self.assertEqual(self.store.history(), [])

    def test_expected_character_is_checked_inside_action_transaction(self):
        self.store.create("B", "male-friend")
        before = self.store.status()
        with self.assertRaises(ValueError):
            self.store.act("water", expected_character_id=self.a["id"])
        self.assertEqual(self.store.status(), before)


if __name__ == "__main__":
    unittest.main()
