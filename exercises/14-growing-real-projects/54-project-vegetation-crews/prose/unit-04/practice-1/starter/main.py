"""Run: plan the tiny season and print the vegetation manager's report.

The season is GridCap tiny, six circuits of a fictional utility, drawn by vegcrew/generate.py from
seed 54. Nothing is read from the working directory, so the report is the same wherever Run starts.
The planner searches with one worker here: four workers that race may return another of the tiny
season's equally good plans from one run to the next.
"""

from __future__ import annotations

from vegcrew import planner
from vegcrew.__main__ import main

if __name__ == "__main__":
    planner.WORKERS = 1                            # one search worker: the same plan every run
    main(["tiny", "--seed", "54"])
