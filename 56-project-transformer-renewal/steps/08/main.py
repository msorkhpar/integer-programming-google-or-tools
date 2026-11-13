"""Run: the finance report for a tiny fleet, written by the `renewal` command.

The fleet is GridCap's and invented: 25 transformers drawn by renewal/fleet.py from seed 56, with a
budget scaled down to its size and the command's default gap, so the solve is quick. Nothing is
read from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

import sys

from renewal.cli import main

if __name__ == "__main__":
    sys.exit(main(["--units", "25", "--seed", "56", "--budget", "2000"]))
