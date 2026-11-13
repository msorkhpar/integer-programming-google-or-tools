"""Lesson 14.1.4: risk that grows while a circuit waits. One circuit's table of risk carried by end week,
the knapsack-era plan (steps/03) priced by the new rule, the new planner's plan (steps/04), and the
end-week domain of a circuit longer than the season.

The small season no longer solves to proven optimality in the planner's 10 seconds. So that this
page's numbers repeat, the small season is solved here with one worker, a fixed seed and a limit on
deterministic time (lesson 4.6.3) instead of the planner's own settings; lesson 14.1.7 makes the
planner itself repeat.
"""

from snapshots import solve_repeatably, use

use(3)
from vegcrew import planner as planner_3          # noqa: E402
from vegcrew.data import season_from_dict as load_3  # noqa: E402
from vegcrew.generate import scenario as scenario_3  # noqa: E402

planner_3.WORKERS = 1
old = {size: planner_3.make_plan(load_3(scenario_3(size))) for size in ("tiny", "small")}

use(4)
from vegcrew.data import DEFER_WEEKS, season_from_dict   # noqa: E402
from vegcrew.generate import scenario                    # noqa: E402
from vegcrew import planner                       # noqa: E402
from vegcrew.planner import horizon, make_plan    # noqa: E402
from vegcrew.report import format_plan                   # noqa: E402
from ortools.sat.python import cp_model                  # noqa: E402

small = season_from_dict(scenario("small"))
c = small.circuit("C17")
h = horizon(small)
print(f"{c.cid}: ${c.risk}k a year (${c.risk / 52:.2f}k a week at week 0), growing ${c.growth}k a week")
print("  trim ends at week   " + "".join(f"{e:>6}" for e in (4, 8, 12, 16, 20, 24, h + DEFER_WEEKS)))
print("  risk carried ($k)   " + "".join(f"{c.carried(e):>6}" for e in (4, 8, 12, 16, 20, 24, h + DEFER_WEEKS)))


def priced(season, plan):
    """The risk a plan carries under the new rule, whatever objective chose it."""
    return sum(c.carried(plan.trims[c.cid].end) if c.cid in plan.trims else c.carried(horizon(season) + DEFER_WEEKS)
               for c in season.circuits)


tiny = season_from_dict(scenario("tiny"))
print(format_plan(tiny, make_plan(tiny)))
print(f"the knapsack-era plan of steps/03 for tiny carries ${priced(tiny, old['tiny']):,}k")

plan, solver = solve_repeatably(planner, small)
print(format_plan(small, plan))
gap = (solver.objective_value - solver.best_objective_bound) / solver.objective_value
print(f"proved: no plan carries less than ${solver.best_objective_bound:,.0f}k (gap {gap:.1%}); "
      f"{solver.num_branches:,} branches")
print(f"the knapsack-era plan of steps/03 for small carries ${priced(small, old['small']):,}k")

# A circuit longer than the season: the first piece of its end-week domain, [weeks, h], is inverted.
too_long = season_from_dict({"budget": 100, "crews": 1, "months": 1, "circuits": [
    {"id": "L1", "region": "North", "miles": 30, "cost": 10, "risk": 52, "weeks": 6, "growth": 0}]})
tm = planner.build(too_long)
h = horizon(too_long)
pieces = [[6, h], [h + DEFER_WEEKS, h + DEFER_WEEKS]]
print(f"a 6-week trim in a {h}-week season: Domain.from_intervals({pieces}) is {cp_model.Domain.from_intervals(pieces)}")
print(f"  e_L1 in the model: {list(tm.model.proto.variables[tm.end['L1'].index].domain)}; "
      f"validate() reports {tm.model.validate() or 'nothing'}")
plan = make_plan(too_long)
print(f"  {plan.status}: {len(plan.trims)} trims, risk carried ${plan.risk_carried}k")
