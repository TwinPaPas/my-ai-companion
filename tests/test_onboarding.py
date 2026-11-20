import contextlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from sai.cli import main
from sai.store import Store


class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name)

    def start(self, answers=(), backend="claude", resolver=None, replies=(), as_json=False):
        output = io.StringIO()
        args = ["--home", self.tmp.name] + (["--json"] if as_json else []) + ["start"]
        if backend:
            args += ["--backend", backend]
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output), \
                patch("builtins.input", side_effect=answers), \
                patch("sai.backends.resolve_executable", side_effect=resolver, return_value=sys.executable), \
                patch("sai.backends.CLIBackend.generate", side_effect=replies):
            try:
                code = main(args)
            except SystemExit as exc:
                code = exc.code
        return code, output.getvalue()

    def test_new_character_reaches_real_chat_loop_and_saves_reply(self):
        code, output = self.start(["Ari", "", "", "noodles", "cucumber", "Hello", "/quit"],
                                  replies=['{"action":"talk","detail":""}', "Hey, good to see you."])
        self.assertEqual(code, 0, output)
        state = self.store.status()
        self.assertEqual((state["name"], state["role"], state["temperament"]), ("Ari", "female-friend", "playful"))
        self.assertEqual(state["likes"], ["noodles"])
        self.assertEqual(self.store.history()[0]["reply"], "Hey, good to see you.")

    def test_default_resume_preserves_memory_and_enables_off_character(self):
        old = self.store.create("Old", "lover")
        self.store.remember("I like jazz")
        self.store.off()
        code, output = self.start(["", "/quit"])
        self.assertEqual(code, 0, output)
        self.assertEqual(self.store.status()["id"], old["id"])
        self.assertTrue(self.store.status()["enabled"])
        self.assertEqual(self.store.memories()[0]["text"], "I like jazz")
        self.assertEqual(len(self.store.list()), 1)

    def test_choose_existing_character_does_not_mix_memories(self):
        first = self.store.create("First", "male-friend")
        self.store.remember("first memory")
        self.store.create("Second", "lover")
        self.store.remember("second memory")
        code, output = self.start(["1", "/quit"])
        self.assertEqual(code, 0, output)
        self.assertEqual(self.store.status()["id"], first["id"])
        self.assertEqual([m["text"] for m in self.store.memories()], ["first memory"])

    def test_cancel_new_character_preserves_existing_off_state(self):
        self.store.create("Old", "lover")
        self.store.off()
        before = self.store.status()
        code, output = self.start(["n", "New", "", EOFError()])
        self.assertEqual(code, 0, output)
        self.assertEqual(self.store.status(), before)
        self.assertEqual(len(self.store.list()), 1)

    def test_cancel_before_creation_leaves_no_database(self):
        code, output = self.start(["Ari", "", "", EOFError()])
        self.assertEqual(code, 0, output)
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())

    def test_invalid_answers_reprompt_before_creating_custom_character(self):
        code, output = self.start(["x" * 61, "Ari", "bad", "4", "", "An old study partner", "99", "2", "", "", "/quit"])
        self.assertEqual(code, 0, output)
        state = self.store.status()
        self.assertEqual((state["role"], state["temperament"], state["backstory"]), ("custom", "warm", "An old study partner"))
        self.assertEqual(len(self.store.list()), 1)

    def test_missing_backend_fails_before_any_state_or_prompt(self):
        code, output = self.start(backend=None, resolver=RuntimeError("CLI not found"))
        self.assertEqual(code, 1, output)
        self.assertIn("CLI not found", output)
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())

    def test_two_available_backends_are_selected_before_setup(self):
        code, output = self.start(["2", "Ari", "", "", "", "", "/quit"], backend=None)
        self.assertEqual(code, 0, output)
        self.assertIn("codex", output)
        self.assertEqual(len(self.store.list()), 1)

    def test_json_start_is_rejected_without_creating_state(self):
        code, output = self.start(as_json=True)
        self.assertEqual(code, 1, output)
        self.assertIn("error", json.loads(output))
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())

    def test_nonexecutable_backend_does_not_create_character(self):
        invalid = Path(self.tmp.name) / "not-a-cli.txt"
        invalid.write_text("This is not an executable.", encoding="utf-8")
        output = io.StringIO()
        with patch.dict(os.environ, {"SAI_CLAUDE_BIN": str(invalid)}), \
                patch("builtins.input", side_effect=["New", "", "", "", "", "/quit"]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = main(["--home", self.tmp.name, "start", "--backend", "claude"])
        self.assertEqual(code, 1, output.getvalue())
        self.assertFalse((Path(self.tmp.name) / "state.db").exists())

    def test_nonexecutable_backend_does_not_enable_off_character(self):
        self.store.create("Existing", "lover")
        self.store.off()
        before = self.store.status()
        invalid = Path(self.tmp.name) / "not-a-cli.txt"
        invalid.write_text("This is not an executable.", encoding="utf-8")
        output = io.StringIO()
        with patch.dict(os.environ, {"SAI_CLAUDE_BIN": str(invalid)}), \
                patch("builtins.input", side_effect=["", "/quit"]), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = main(["--home", self.tmp.name, "start", "--backend", "claude"])
        self.assertEqual(code, 1, output.getvalue())
        self.assertEqual(self.store.status(), before)


if __name__ == "__main__":
    unittest.main()
