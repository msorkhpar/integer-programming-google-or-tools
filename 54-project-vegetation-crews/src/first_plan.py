"""Lesson 14.1.1: the first plan, a knapsack over GridCap's (fictional) circuits, against the ranking
a spreadsheet would make: sort by risk removed per $k and fund down the list until the money runs out."""

from snapshots import use

use(0)
from vegcrew.data import season_from_dict          # noqa: E402  (imported from the snapshot just chosen)
from vegcrew.generate import scenario              # noqa: E402
from vegcrew.planner import make_plan              # noqa: E402
from vegcrew.report import format_plan             # noqa: E402

season = season_from_dict(scenario("small"))
print("steps/00:")
print(format_plan(season, make_plan(season)))

use(1)
from vegcrew.data import season_from_dict          # noqa: E402  (imported from the snapshot just chosen)
from vegcrew.generate import scenario              # noqa: E402
from vegcrew.planner import build, make_plan       # noqa: E402
from vegcrew.report import format_plan             # noqa: E402

season = season_from_dict(scenario("small"))
plan = make_plan(season)
print("steps/01:")
print(format_plan(season, plan))


def ranked(season):
    """Fund circuits in order of risk per $k, skipping any that no longer fit."""
    left, chosen = season.budget, []
    for c in sorted(season.circuits, key=lambda c: c.risk / c.cost, reverse=True):
        if c.cost <= left:
            chosen.append(c)
            left -= c.cost
    return chosen


greedy = ranked(season)
print(f"ranking by risk per $k: {len(greedy)} trims, cost ${sum(c.cost for c in greedy):,}k, "
      f"risk removed ${sum(c.risk for c in greedy):,}k a year")
print("in the plan, not the ranking:", " ".join(sorted(set(plan.trims) - {c.cid for c in greedy})))
print("in the ranking, not the plan:", " ".join(sorted({c.cid for c in greedy} - set(plan.trims))))
model, x = build(season)
print(f"model: {model.get_num_variables()} binary variables, {model.get_num_linear_constraints()} row")
