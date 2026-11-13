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
    with conn:
        conn.execute("DELETE FROM estimate_line WHERE estimate_id IN "
                     "(SELECT estimate_id FROM estimate WHERE project = ?)", (project,))
        conn.execute("DELETE FROM estimate WHERE project = ?", (project,))
        estimate_id = conn.execute("INSERT INTO estimate (project) VALUES (?)", (project,)).lastrowid
        for item, amount in lines:
            conn.execute("INSERT INTO estimate_line VALUES (?, ?, ?)", (estimate_id, item, amount))
    return estimate_id


if __name__ == "__main__":
    conn = connect(":memory:")
    conn.executescript(SCHEMA)
    print(save_estimate(conn, "Elm Street main", [("pipe", 120), ("paving", 40)]))
