"""Run: plan the demo export and print the planners' report.

data/demo.json is GridCap tiny, a fictional utility's portfolio. Its path is taken from this
file's folder, never from the working directory, so the report is the same wherever Run starts.
"""

from __future__ import annotations

from pathlib import Path

from cipt.__main__ import main

DEMO = Path(__file__).resolve().parent / "data" / "demo.json"

if __name__ == "__main__":
    raise SystemExit(main([str(DEMO)]))
