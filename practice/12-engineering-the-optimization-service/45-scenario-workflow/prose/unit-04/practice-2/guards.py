from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE budget_plan (
    plan_id     TEXT PRIMARY KEY,
    fiscal_year INTEGER NOT NULL,
    status      TEXT NOT NULL CHECK (status IN ('draft', 'approved')),
    amount      INTEGER NOT NULL
) STRICT;
"""

GUARDS = """
-- TODO: the index and triggers that keep the rules.
"""


def open_db() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:", autocommit=True)
    conn.executescript(SCHEMA + GUARDS)
    return conn


if __name__ == "__main__":
    conn = open_db()
    conn.execute("INSERT INTO budget_plan VALUES ('B-1', 2028, 'approved', 4200)")
    print(conn.execute("SELECT * FROM budget_plan").fetchall())
