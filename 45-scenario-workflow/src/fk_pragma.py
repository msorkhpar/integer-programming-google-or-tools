"""Lesson 12.1.4: PRAGMA foreign_keys takes effect only outside a transaction, and sqlite3 may have opened one.

No GridCap data here: an in-memory database with one parent and one child table.
"""

import sqlite3
import sys

print("Python", sys.version.split()[0], "  SQLite library", sqlite3.sqlite_version)

SCHEMA = "CREATE TABLE scenario (id TEXT PRIMARY KEY); CREATE TABLE run (id INTEGER PRIMARY KEY, scenario_id TEXT REFERENCES scenario (id));"


def try_orphan(conn: sqlite3.Connection, label: str) -> None:
    enabled = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    try:
        conn.execute("INSERT INTO run (scenario_id) VALUES ('S-999')")
        outcome = "orphan run stored"
    except sqlite3.IntegrityError as e:
        outcome = f"refused: {e}"
    print(f"{label:<40} foreign_keys={enabled}  {outcome}")


conn = sqlite3.connect(":memory:", autocommit=False)
conn.execute("PRAGMA foreign_keys = ON")
print("autocommit=False opens a transaction at once:", conn.in_transaction)
conn.executescript(SCHEMA)
try_orphan(conn, "pragma sent inside that transaction")

conn = sqlite3.connect(":memory:", autocommit=True)
conn.execute("PRAGMA foreign_keys = ON")
conn.autocommit = False
conn.executescript(SCHEMA)
try_orphan(conn, "pragma sent first, then autocommit=False")
