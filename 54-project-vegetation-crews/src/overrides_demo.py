"""Lesson 14.1.6: planner overrides on the small season, one set the plan can keep and two it cannot,
with the explanation the planner returns. WORKERS is set to 1 so that this page's output repeats."""

from ortools.sat.python import cp_model

from snapshots import use

use(6)
from vegcrew import planner                        # noqa: E402
from vegcrew.data import Override, season_from_dict  # noqa: E402
from vegcrew.explain import conflict               # noqa: E402
from vegcrew.generate import scenario              # noqa: E402
from vegcrew.model import build                    # noqa: E402
from vegcrew.report import format_plan             # noqa: E402

planner.WORKERS = 1
season = season_from_dict(scenario("small"))
base = planner.make_plan(season)
print(f"no overrides: {base.status}, risk carried ${base.risk_carried:,}k")

kept = (Override("skip", "C17", reason="county closes the road until October"),
        Override("pin", "C02", crew="K2", start=0, reason="complaints near the school"))
plan = planner.make_plan(season, kept)
print(format_plan(season, plan))
print(f"the two overrides cost ${plan.risk_carried - base.risk_carried:,}k of risk")

clash = (Override("pin", "C17", crew="K1", start=0, reason="crew already on site"),
         Override("pin", "C02", crew="K1", start=5, reason="complaints near the school"))
report = format_plan(season, planner.make_plan(season, clash)).splitlines()
print("\n".join(report[1:2] + report[-3:]))

money = tuple(Override("force", cid, reason=why) for cid, why in [
    ("C08", "storm damage"), ("C11", "fire-risk area"), ("C14", "customer complaints"),
    ("C01", "regulator letter"), ("C19", "new subdivision")])
report = format_plan(season, planner.make_plan(season, money)).splitlines()
print("\n".join(report[1:2] + report[-9:]))
musts = [c for c in season.circuits if c.must]
asked = musts + [season.circuit(o.cid) for o in money]
print(f"the arithmetic: {' + '.join(str(c.cost) for c in asked)} = ${sum(c.cost for c in asked):,}k "
      f"> ${season.budget:,}k")

# What the solver names before the deletion filter, against what the filter keeps.
tm = build(season, money)
tm.model.add_assumptions(list(tm.rules.values()))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.solve(tm.model)
print(f"rules behind literals: {len(tm.rules)}; named by the solver: "
      f"{len(solver.sufficient_assumptions_for_infeasibility())}; after the deletion filter: "
      f"{len(conflict(build(season, money)))}")
