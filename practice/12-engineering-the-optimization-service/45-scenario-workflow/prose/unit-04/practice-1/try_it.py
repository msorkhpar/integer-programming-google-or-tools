"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import os
import sqlite3
import tempfile

from estimate import SCHEMA, connect, save_estimate

with tempfile.TemporaryDirectory() as folder:
    conn = connect(os.path.join(folder, "estimates.db"))
    conn.executescript(SCHEMA)
    conn.commit()

    def lines(project):
        return conn.execute("SELECT l.item, l.amount FROM estimate_line AS l JOIN estimate AS e "
                            "USING (estimate_id) WHERE e.project = ?", (project,)).fetchall()

    print("save Oak Lane culvert:", save_estimate(conn, "Oak Lane culvert", [("culvert", 75), ("grading", 20)]))
    print("lines:", lines("Oak Lane culvert"))
    try:
        save_estimate(conn, "Oak Lane culvert", [("culvert", 60), ("refund", -5)])
    except sqlite3.IntegrityError as e:
        print("revision with -5 raised:", e)
    print("lines after it:", lines("Oak Lane culvert"))
    save_estimate(conn, "Oak Lane culvert", [("culvert", 80)])
    print("lines after a revision to 80:", lines("Oak Lane culvert"))
    conn.close()
