"""Run: plan the tiny season and print the vegetation manager's report, then the same season under a
planner's override it can keep and under two overrides that clash.

The season is GridCap tiny, six circuits of a fictional utility, drawn by vegcrew/generate.py from
seed 54. Nothing is read from the working directory, so the report is the same wherever Run starts.
The planner searches with one worker here, as in steps/03, so that Run repeats the same search on
every run.
"""

from __future__ import annotations

from vegcrew import planner
from vegcrew.__main__ import main
from vegcrew.data import Override, season_from_dict
from vegcrew.generate import scenario
from vegcrew.planner import make_plan
from vegcrew.report import format_plan

SIZE, SEED = "tiny", 54


def show_overrides() -> None:
    """The plan with one override it keeps, then the rules named when two overrides clash."""
    season = season_from_dict(scenario(SIZE, SEED))
    kept = (Override("skip", "C03", reason="road closed"),)
    clash = (Override("pin", "C01", crew="K1", start=12, reason="crew is nearby"),
             Override("pin", "C05", crew="K1", start=13, reason="landowner asked"))
    for title, overrides in (("skip C03:", kept), ("pin C01 and C05 a week apart on K1:", clash)):
        print()
        print(title)
        print(format_plan(season, make_plan(season, overrides)))


if __name__ == "__main__":
    planner.WORKERS = 1                            # one search worker: the same plan every run
    main([SIZE, "--seed", str(SEED)])
    show_overrides()
