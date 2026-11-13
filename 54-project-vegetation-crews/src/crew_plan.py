"""Lesson 14.1.3: the interval model's plan for the small and tiny seasons, one line per crew.

The planner searches with four workers, which can return a different one of several equally good
plans from run to run (lesson 14.1.7 is about that). So that this page's output repeats, this program
sets the snapshot's WORKERS to 1 before it plans. Last, it plans the tiny season again with the same model
built from the circuits in reverse order.
"""

from snapshots import use

use(3)
from vegcrew import planner                        # noqa: E402
from vegcrew.data import season_from_dict          # noqa: E402
from vegcrew.generate import scenario              # noqa: E402
from vegcrew.report import format_plan             # noqa: E402

planner.WORKERS = 1
for size in ("small", "tiny"):
    season = season_from_dict(scenario(size))
    print(format_plan(season, planner.make_plan(season)))
tm = planner.build(season_from_dict(scenario("small")))
proto = tm.model.proto
print(f"small model: {len(proto.variables)} variables, {len(proto.constraints)} constraints "
      f"({len(tm.work)} optional intervals)")

tiny = season_from_dict(scenario("tiny"))
built_in_order = planner.build
planner.build = lambda season: built_in_order(
    type(season)(season.name, season.budget, season.crews, season.months, tuple(reversed(season.circuits))))
print("tiny, the same model built from the circuits in reverse order:")
print(format_plan(tiny, planner.make_plan(tiny)).splitlines()[-1])
