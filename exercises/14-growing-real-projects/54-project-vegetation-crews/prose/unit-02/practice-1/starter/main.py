"""Run: plan the tiny season and print the vegetation manager's report.

The season is GridCap tiny, six circuits of a fictional utility, drawn by vegcrew/generate.py from
seed 54. Nothing is read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from vegcrew.__main__ import main

if __name__ == "__main__":
    main(["tiny", "--seed", "54"])
