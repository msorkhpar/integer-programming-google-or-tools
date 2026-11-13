from __future__ import annotations

import sqlite3

SCHEMA = """
CREATE TABLE run_start (run_id INTEGER NOT NULL, project TEXT NOT NULL, start_year INTEGER NOT NULL,
                        PRIMARY KEY (run_id, project)) STRICT;
CREATE TABLE cost (project TEXT NOT NULL, year_offset INTEGER NOT NULL, amount INTEGER NOT NULL,
                   PRIMARY KEY (project, year_offset)) STRICT;
"""

SPEND_DIFF = """
WITH spend AS (
    SELECT r.run_id, r.start_year + c.year_offset AS year, sum(c.amount) AS amount
    FROM run_start AS r JOIN cost AS c ON c.project = r.project
    WHERE r.run_id IN (:a, :b)
    GROUP BY r.run_id, year
)
SELECT coalesce(a.year, b.year) AS year, coalesce(a.amount, 0) AS a_spend, coalesce(b.amount, 0) AS b_spend
FROM (SELECT year, amount FROM spend WHERE run_id = :a) AS a
FULL OUTER JOIN (SELECT year, amount FROM spend WHERE run_id = :b) AS b ON a.year = b.year
WHERE coalesce(a.amount, 0) <> coalesce(b.amount, 0)
ORDER BY year
"""


def spend_diff(conn: sqlite3.Connection, a: int, b: int) -> list[tuple[int, int, int]]:
    """(year, run a's spend, run b's spend) for every year whose spend differs, in year order."""
    return [tuple(row) for row in conn.execute(SPEND_DIFF, {"a": a, "b": b})]


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO cost VALUES (?, ?, ?)", [("M-1", 0, 300), ("M-1", 1, 200)])
    conn.executemany("INSERT INTO run_start VALUES (?, ?, ?)", [(1, "M-1", 2027), (2, "M-1", 2028)])
    print(spend_diff(conn, 1, 2))
