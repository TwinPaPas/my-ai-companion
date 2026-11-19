import concurrent.futures
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from sai.store import Store


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        self.store = Store(self.home)

    def create(self):
        return self.store.create("하루", "lover", boundaries=["외모"])

    def test_create_and_reopen_preserve_personality_and_concern(self):
        character = self.create()
        self.store.act("tease", "외모")
        loaded = Store(self.home).status()
        self.assertEqual(loaded["id"], character["id"])
        self.assertEqual(loaded["concern"], "외모")
        self.assertEqual(loaded["name"], "하루")

    def test_off_survives_reopen_and_prevents_actions(self):
        character = self.create()
        self.store.off()
        reopened = Store(self.home)
        self.assertFalse(reopened.status()["enabled"])
        with self.assertRaises(ValueError):
            reopened.act("water")
        reopened.use(character["id"])
        self.assertTrue(reopened.status()["enabled"])

    def test_duplicate_event_id_does_not_apply_twice(self):
        self.create()
        self.store.act("tease", "외모", event_id="turn-1")
        before = self.store.status()
        r = self.store.act("tease", "외모", event_id="turn-1")
        self.assertTrue(r["duplicate"])
        self.assertEqual(self.store.status(), before)

    def test_concurrent_memories_do_not_lose_updates(self):
        self.create()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda i: Store(self.home).remember(f"취향 {i}"), range(12)))
        self.assertEqual(len(self.store.memories()), 12)

    def test_memory_is_explicit_and_can_be_removed(self):
        self.create()
        entry = self.store.remember("나는 민트초코를 좋아해")
        self.store.forget(entry["id"])
        self.assertEqual(self.store.memories(), [])

    def test_empty_status_is_read_only(self):
        self.assertIsNone(self.store.status())
        self.assertFalse((self.home / "state.db").exists())

    def test_unknown_schema_is_rejected_without_reset(self):
        self.create()
        with closing(sqlite3.connect(self.home / "state.db")) as db:
            db.execute("PRAGMA user_version=999")
        with self.assertRaisesRegex(ValueError, "schema"):
            self.store.status()
        with closing(sqlite3.connect(self.home / "state.db")) as db:
            self.assertEqual(db.execute("PRAGMA user_version").fetchone()[0], 999)


if __name__ == "__main__":
    unittest.main()
