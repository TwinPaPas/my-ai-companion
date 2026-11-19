import json
import subprocess
import sys
import unittest

from sai.backends import extract_reply, run_command, build_command


class BackendTests(unittest.TestCase):
    def test_shell_characters_are_sent_on_stdin_not_evaluated(self):
        message = '한글 $(whoami) `echo hidden` & ; "quotes"'
        output = run_command([sys.executable, "-c", "import sys;sys.stdout.buffer.write(sys.stdin.buffer.read())"], message, 10)
        self.assertEqual(output, message)

    def test_nonzero_is_a_failure_not_a_reply(self):
        with self.assertRaisesRegex(RuntimeError, "exit 3"):
            run_command([sys.executable, "-c", "import sys; print('not a reply');sys.exit(3)"], "test", 10)

    def test_timeout_is_visible(self):
        with self.assertRaisesRegex(RuntimeError, "timed out"):
            run_command([sys.executable, "-c", "import time; time.sleep(3)"], "test", 0.1)

    def test_codex_events_select_only_final_assistant_output(self):
        rows = [dict(type="thread.started", thread_id="id"),
                dict(type="item.completed", item={"type": "reasoning", "text": "private"}),
                dict(type="item.completed", item={"type": "agent_message", "text": "안녕"}),
                dict(type="turn.completed", usage={})]
        self.assertEqual(extract_reply("codex", "\n".join(json.dumps(r) for r in rows)), "안녕")

    def test_model_errors_and_empty_output_fail(self):
        for host, text in [("codex", '{"type":"turn.failed","error":{"message":"denied"}}'),
                           ("claude", '{"is_error":true,"result":"bad"}'),
                           ("claude", '{"result":""}')]:
            with self.assertRaises(RuntimeError):
                extract_reply(host, text)

    def test_arguments_do_not_disable_native_permissions_or_hook_trust(self):
        for host in ["codex", "claude"]:
            command = build_command(host, executable=host)
            self.assertFalse(any("dangerously" in arg for arg in command))
        self.assertIn("read-only", build_command("codex", executable="codex"))


if __name__ == "__main__":
    unittest.main()
