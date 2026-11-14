"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import sqlite3

from guards import open_db

conn = open_db()


def attempt(sql):
    try:
        conn.execute(sql)
        return "accepted"
    except sqlite3.IntegrityError as e:
        return f"refused ({e})"


print("insert P-1 2031 approved:", attempt("INSERT INTO budget_plan VALUES ('P-1', 2031, 'approved', 5100)"))
print("insert P-2 2031 draft:", attempt("INSERT INTO budget_plan VALUES ('P-2', 2031, 'draft', 5000)"))
print("insert P-3 2031 approved:", attempt("INSERT INTO budget_plan VALUES ('P-3', 2031, 'approved', 4800)"))
print("edit P-2 amount:", attempt("UPDATE budget_plan SET amount = 4950 WHERE plan_id = 'P-2'"))
print("edit P-1 amount:", attempt("UPDATE budget_plan SET amount = 5200 WHERE plan_id = 'P-1'"))
print("delete P-1:", attempt("DELETE FROM budget_plan WHERE plan_id = 'P-1'"))
print("rows:", conn.execute("SELECT * FROM budget_plan ORDER BY plan_id").fetchall())
