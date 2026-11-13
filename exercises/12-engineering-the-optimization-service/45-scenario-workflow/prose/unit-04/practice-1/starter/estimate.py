from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE estimate (estimate_id INTEGER PRIMARY KEY, project TEXT NOT NULL UNIQUE) STRICT;
CREATE TABLE estimate_line (
    estimate_id INTEGER NOT NULL REFERENCES estimate (estimate_id),
    item        TEXT NOT NULL,
    amount      INTEGER NOT NULL CHECK (amount >= 0)
) STRICT;
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, autocommit=True)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.autocommit = False
    return conn


def save_estimate(conn: sqlite3.Connection, project: str, lines: list[tuple[str, int]]) -> int:
    """Store the project's estimate, replacing any earlier one; all of it is committed, or none."""
    # TODO: replace the project's estimate so that all of it is committed, or none of it.
    return 0


if __name__ == "__main__":
    conn = connect(":memory:")
    conn.executescript(SCHEMA)
    print(save_estimate(conn, "Elm Street main", [("pipe", 120), ("paving", 40)]))
