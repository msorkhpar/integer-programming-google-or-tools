import sqlite3

from guards import open_db


def refused(conn, sql: str) -> bool:
    try:
        conn.execute(sql)
        return False
    except sqlite3.IntegrityError:
        return True


def test_a_year_takes_one_approved_plan():
    conn = open_db()
    assert not refused(conn, "INSERT INTO budget_plan VALUES ('B-1', 2028, 'approved', 4200)")
    assert not refused(conn, "INSERT INTO budget_plan VALUES ('B-2', 2029, 'approved', 4300)")
    assert refused(conn, "INSERT INTO budget_plan VALUES ('B-3', 2028, 'approved', 3900)")


def test_drafts_of_one_year_coexist_with_its_approved_plan():
    conn = open_db()
    conn.execute("INSERT INTO budget_plan VALUES ('B-1', 2028, 'approved', 4200)")
    assert not refused(conn, "INSERT INTO budget_plan VALUES ('B-4', 2028, 'draft', 4000)")
    assert not refused(conn, "INSERT INTO budget_plan VALUES ('B-5', 2028, 'draft', 4100)")
    assert refused(conn, "UPDATE budget_plan SET status = 'approved' WHERE plan_id = 'B-4'")


def test_a_draft_is_edited_but_an_approved_plan_is_frozen():
    conn = open_db()
    conn.execute("INSERT INTO budget_plan VALUES ('B-1', 2028, 'approved', 4200)")
    conn.execute("INSERT INTO budget_plan VALUES ('B-6', 2030, 'draft', 4000)")
    assert not refused(conn, "UPDATE budget_plan SET amount = 3950 WHERE plan_id = 'B-6'")
    assert not refused(conn, "UPDATE budget_plan SET status = 'approved' WHERE plan_id = 'B-6'")
    assert refused(conn, "UPDATE budget_plan SET amount = 4500 WHERE plan_id = 'B-1'")


def test_an_approved_plan_cannot_be_deleted():
    conn = open_db()
    conn.execute("INSERT INTO budget_plan VALUES ('B-1', 2028, 'approved', 4200)")
    conn.execute("INSERT INTO budget_plan VALUES ('B-7', 2029, 'draft', 4000)")
    assert not refused(conn, "DELETE FROM budget_plan WHERE plan_id = 'B-7'")
    assert refused(conn, "DELETE FROM budget_plan WHERE plan_id = 'B-1'")
