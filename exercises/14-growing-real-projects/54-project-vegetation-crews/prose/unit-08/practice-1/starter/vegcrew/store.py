"""Plans kept in a SQLite file: each stored once, as its record, under a number."""

from __future__ import annotations

import json
import sqlite3
import threading

from vegcrew.record import dumps


class Store:
    def __init__(self, path: str = ":memory:"):
        # FastAPI runs plain `def` endpoints on worker threads, so one connection is shared under a lock.
        self.db = sqlite3.connect(path, check_same_thread=False)
        self.lock = threading.Lock()
        with self.lock, self.db:
            self.db.execute("CREATE TABLE IF NOT EXISTS plans ("
                            "id INTEGER PRIMARY KEY, input_sha256 TEXT NOT NULL, record TEXT NOT NULL)")

    def save(self, record: dict) -> int:
        with self.lock, self.db:
            cursor = self.db.execute("INSERT INTO plans (input_sha256, record) VALUES (?, ?)",
                                     (record["input_sha256"], dumps(record)))
            return cursor.lastrowid

    def get(self, plan_id: int) -> dict | None:
        with self.lock:
            row = self.db.execute("SELECT record FROM plans WHERE id = ?", (plan_id,)).fetchone()
        return json.loads(row[0]) if row else None
