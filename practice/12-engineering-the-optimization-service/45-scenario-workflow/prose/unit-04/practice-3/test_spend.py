import sqlite3

from spend import SCHEMA, spend_diff

COST = [("M-1", 0, 300), ("M-1", 1, 200), ("M-2", 0, 250), ("M-3", 0, 350), ("M-4", 0, 200), ("M-4", 1, 200)]


def db(runs: dict[int, dict[str, int]]) -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO cost VALUES (?, ?, ?)", COST)
    conn.executemany("INSERT INTO run_start VALUES (?, ?, ?)",
                     [(run, p, t) for run, plan in runs.items() for p, t in plan.items()])
    return conn


def test_years_whose_spend_changed_are_listed_and_equal_years_are_not():
    conn = db({1: {"M-2": 2027, "M-3": 2028, "M-1": 2029}, 2: {"M-3": 2027, "M-2": 2028, "M-1": 2029}})
    assert spend_diff(conn, 1, 2) == [(2027, 250, 350), (2028, 350, 250)]


def test_a_year_only_the_second_run_spends_in_is_listed():
    conn = db({1: {"M-2": 2027}, 2: {"M-2": 2027, "M-3": 2029}})
    assert spend_diff(conn, 1, 2) == [(2029, 0, 350)]


def test_a_year_only_the_first_run_spends_in_is_listed_with_zero():
    conn = db({1: {"M-2": 2027, "M-3": 2028}, 2: {"M-2": 2027}, 3: {"M-3": 2027}})
    assert spend_diff(conn, 1, 2) == [(2028, 350, 0)]


def test_later_years_of_work_count_in_their_own_year():
    conn = db({1: {"M-1": 2027, "M-4": 2027}, 2: {"M-1": 2027, "M-4": 2028}})
    assert spend_diff(conn, 1, 2) == [(2027, 500, 300), (2029, 0, 200)]
