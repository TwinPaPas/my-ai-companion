"""Transactional local state shared by CLI processes and host sessions."""
from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

from .engine import apply_action, checked_text, new_character

SCHEMA = """
CREATE TABLE IF NOT EXISTS characters (id TEXT PRIMARY KEY, state TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, character_id TEXT NOT NULL, result TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS memories (id TEXT PRIMARY KEY, character_id TEXT NOT NULL, text TEXT NOT NULL, created REAL NOT NULL);
CREATE TABLE IF NOT EXISTS turns (id INTEGER PRIMARY KEY, character_id TEXT NOT NULL, user TEXT NOT NULL, reply TEXT NOT NULL, created REAL NOT NULL);
"""


class Store:
    def __init__(self, home=None):
        self.home = Path(home or os.environ.get("SAI_HOME") or Path.home() / ".sai").expanduser()
        self.path = self.home / "state.db"

    @contextmanager
    def connection(self, write=False):
        if not self.path.exists() and not write:
            yield None
            return
        if write:
            self.home.mkdir(parents=True, exist_ok=True, mode=0o700)
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            if write:
                db.execute("BEGIN IMMEDIATE")
            version = db.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ValueError(f"Unsupported state schema {version}; data left untouched")
            if version == 0:
                tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                if tables or not write:
                    raise ValueError("Unknown state schema; data left untouched")
                for statement in SCHEMA.split(";"):
                    if statement.strip():
                        db.execute(statement)
                db.execute("PRAGMA user_version=1")
            yield db
            if write:
                db.commit()
        except sqlite3.DatabaseError as exc:
            db.rollback()
            raise ValueError("Cannot read/write state database; data was not reset") from exc
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def _selected(db, require_enabled=False):
        if db is None:
            return None
        meta = dict(db.execute("SELECT key,value FROM meta").fetchall())
        row = db.execute("SELECT state FROM characters WHERE id=?", (meta.get("active", ""),)).fetchone()
        if row is None:
            return None
        try:
            state = json.loads(row["state"])
        except (json.JSONDecodeError, TypeError) as exc:
            raise ValueError("Invalid character data; data left untouched") from exc
        state["enabled"] = meta.get("enabled") == "1"
        if require_enabled and not state["enabled"]:
            raise ValueError("SAI is off; use a character to resume")
        return state

    @staticmethod
    def _meta(db, key, value):
        db.execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))

    def create(self, name, role, temperament="playful", **kwargs):
        state = new_character(name, role, temperament, **kwargs)
        with self.connection(True) as db:
            db.execute("INSERT INTO characters VALUES(?,?)", (state["id"], json.dumps(state, ensure_ascii=False)))
            self._meta(db, "active", state["id"])
            self._meta(db, "enabled", "1")
        return dict(state, enabled=True)

    def status(self):
        with self.connection() as db:
            return self._selected(db)

    def list(self):
        with self.connection() as db:
            if db is None:
                return []
            return [json.loads(row[0]) for row in db.execute("SELECT state FROM characters ORDER BY rowid")]

    def use(self, character_id):
        with self.connection(True) as db:
            if not db.execute("SELECT 1 FROM characters WHERE id=?", (character_id,)).fetchone():
                raise ValueError("Unknown character id; run sai list")
            self._meta(db, "active", character_id)
            self._meta(db, "enabled", "1")
            return self._selected(db)

    def off(self):
        if not self.path.exists():
            return None
        with self.connection(True) as db:
            self._meta(db, "enabled", "0")
            return self._selected(db)

    def act(self, action, detail="", event_id=None, now=None):
        with self.connection(True) as db:
            state = self._selected(db, True)
            if state is None:
                raise ValueError("Create a character first")
            event_id = checked_text(event_id or uuid.uuid4().hex, "event_id", 256, False)
            key = state["id"] + ":" + event_id
            old = db.execute("SELECT result FROM events WHERE id=?", (key,)).fetchone()
            if old:
                return dict(json.loads(old[0]), duplicate=True)
            new, result = apply_action(state, action, detail, now)
            result.update(state=new, duplicate=False)
            db.execute("UPDATE characters SET state=? WHERE id=?", (json.dumps(new, ensure_ascii=False), state["id"]))
            db.execute("INSERT INTO events VALUES(?,?,?)", (key, state["id"], json.dumps(result, ensure_ascii=False)))
            return result

    def remember(self, text):
        text = checked_text(text, "memory", 500, False)
        with self.connection(True) as db:
            state = self._selected(db, True)
            if not state:
                raise ValueError("Create a character first")
            count = db.execute("SELECT count(*) FROM memories WHERE character_id=?", (state["id"],)).fetchone()[0]
            if count >= 100:
                raise ValueError("Memory limit reached (100); forget an old entry first")
            entry = {"id": uuid.uuid4().hex[:12], "text": text, "created": time.time()}
            db.execute("INSERT INTO memories VALUES(?,?,?,?)", (entry["id"], state["id"], text, entry["created"]))
            return entry

    def memories(self):
        with self.connection() as db:
            state = self._selected(db)
            if not state:
                return []
            return [dict(row) for row in db.execute("SELECT id,text,created FROM memories WHERE character_id=? ORDER BY created", (state["id"],))]

    def forget(self, memory_id):
        with self.connection(True) as db:
            state = self._selected(db)
            if not state:
                raise ValueError("No character selected")
            result = db.execute("DELETE FROM memories WHERE id=? AND character_id=?", (memory_id, state["id"]))
            if not result.rowcount:
                raise ValueError("Unknown memory id")

    def add_turn(self, character_id, user, reply):
        user = checked_text(user, "user message", 8000, False)
        reply = checked_text(reply, "reply", 16000, False)
        with self.connection(True) as db:
            current = self._selected(db, True)
            if not current or current["id"] != character_id:
                raise ValueError("Character changed while the reply was generated; reply was not saved")
            db.execute("INSERT INTO turns(character_id,user,reply,created) VALUES(?,?,?,?)", (character_id, user, reply, time.time()))

    def history(self, limit=8):
        with self.connection() as db:
            state = self._selected(db)
            if not state:
                return []
            rows = db.execute("SELECT user,reply FROM turns WHERE character_id=? ORDER BY id DESC LIMIT ?", (state["id"], max(0, min(20, limit)))).fetchall()
            return [dict(row) for row in reversed(rows)]
