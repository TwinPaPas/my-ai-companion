import json
from pathlib import Path
import unittest

from scripts.render_everyday import scenes


class ShowcaseTests(unittest.TestCase):
    def test_displayed_prompts_and_reply_excerpts_come_from_recording(self):
        root = Path(__file__).resolve().parents[1]
        record = json.loads((root / "docs/verification/everyday-0.1.2-claude-verified.json").read_text(encoding="utf-8"))
        for _, label, prompt, entry, _ in scenes(record):
            if entry is None:
                continue
            with self.subTest(scene=label):
                self.assertIn(prompt, entry["command"][-1])
                quote = entry["excerpt"].removesuffix(" ...")
                self.assertIn(quote, " ".join(entry["reply"].split()))


if __name__ == "__main__":
    unittest.main()
