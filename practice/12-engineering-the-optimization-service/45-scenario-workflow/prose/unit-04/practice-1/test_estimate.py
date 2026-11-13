import sqlite3

from estimate import SCHEMA, connect, save_estimate

GOOD = [("pipe", 120), ("valves", 30), ("paving", 40)]
REVISED = [("pipe", 140), ("paving", 45)]


def db(tmp_path):
    conn = connect(str(tmp_path / "estimates.db"))
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def counts(conn):
    return (conn.execute("SELECT count(*) FROM estimate").fetchone()[0],
            conn.execute("SELECT count(*) FROM estimate_line").fetchone()[0])


def total(conn, project):
    return conn.execute("SELECT sum(l.amount) FROM estimate_line AS l JOIN estimate AS e USING (estimate_id) "
                        "WHERE e.project = ?", (project,)).fetchone()[0]


def test_an_estimate_is_stored_with_its_lines(tmp_path):
    conn = db(tmp_path)
    save_estimate(conn, "Elm Street main", GOOD)
    assert counts(conn) == (1, 3) and total(conn, "Elm Street main") == 190


def test_a_revision_replaces_the_old_estimate(tmp_path):
    conn = db(tmp_path)
    save_estimate(conn, "Elm Street main", GOOD)
    save_estimate(conn, "Elm Street main", REVISED)
    assert counts(conn) == (1, 2) and total(conn, "Elm Street main") == 185


def test_a_bad_revision_keeps_the_old_estimate(tmp_path):
    conn = db(tmp_path)
    save_estimate(conn, "Elm Street main", GOOD)
    try:
        save_estimate(conn, "Elm Street main", [("pipe", 90), ("credit", -15)])
    except sqlite3.IntegrityError:
        pass
    assert counts(conn) == (1, 3) and total(conn, "Elm Street main") == 190


def test_a_project_name_with_a_quote_is_stored_as_written(tmp_path):
    conn = db(tmp_path)
    try:
        eid = save_estimate(conn, "O'Brien Street main", GOOD)
    except sqlite3.Error as e:
        eid = f"raised {type(e).__name__}"
    assert conn.execute("SELECT estimate_id, project FROM estimate").fetchall() == [(eid, "O'Brien Street main")]


def test_another_connection_sees_the_saved_estimate(tmp_path):
    conn = db(tmp_path)
    save_estimate(conn, "Elm Street main", GOOD)
    other = connect(str(tmp_path / "estimates.db"))
    assert counts(other) == (1, 3)
