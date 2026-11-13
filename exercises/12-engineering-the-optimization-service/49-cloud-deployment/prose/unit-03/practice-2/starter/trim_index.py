from __future__ import annotations

import json  # noqa: F401
import sqlite3

from botocore.exceptions import ClientError  # noqa: F401

SCHEMA = """
CREATE TABLE run (
    run_id     TEXT PRIMARY KEY,
    digest     TEXT NOT NULL,
    status     TEXT NOT NULL CHECK (status IN ('submitted', 'optimal', 'time_limit', 'infeasible', 'failed')),
    result_key TEXT,
    cost       INTEGER,
    CHECK ((status = 'submitted') = (result_key IS NULL))
) STRICT;
"""


def connect(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, autocommit=False)
    conn.row_factory = sqlite3.Row
    with conn:
        conn.executescript(SCHEMA)
    return conn


def record(conn: sqlite3.Connection, run_id: str, digest: str) -> None:
    with conn:
        conn.execute("INSERT INTO run (run_id, digest, status) VALUES (?, ?, 'submitted')", (run_id, digest))


def result_key(digest: str, run_id: str) -> str:
    return f"trim-results/{digest}/{run_id}.json"


def poll(conn: sqlite3.Connection, s3, bucket: str, run_id: str) -> str:
    """The run's status; a waiting run is finished in the index when its result object exists."""
    # TODO: read the row; if it waits, look for its result object and record it when it is there.
    return "submitted"


def best_runs(conn: sqlite3.Connection) -> dict[str, str]:
    """For each survey digest, the finished run with a plan and the lowest cost (ties: lowest run id)."""
    return {}
