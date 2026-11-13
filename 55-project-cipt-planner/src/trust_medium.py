"""Lesson 14.2.8: trust at scale on GridCap medium (400 projects, 10 years; a fictional utility).

Plans the medium export three times, once here and twice in fresh processes, and compares the plan
digests; prints the run's manifest; checks the demo export against its golden plan, as shipped and with a
planted regression in the window cut; then plans a 2031 budget cut and a 2031 budget rise, each
cold and warm-started from the base plan. Each medium solve takes tens of seconds; the whole program a few minutes.
"""

import json
import subprocess
import sys
from pathlib import Path

from export import gridcap_export
from steps import STEPS, use

raw = gridcap_export("medium")
cipt = use(8)
request = cipt.data.load_request(raw)
base = cipt.solve.solve(request)
print(f"medium: {len(cipt.model.build(request).x)} binary variables, base plan funds {len(base.starts)} "
      f"projects, NPV ${base.npv:,.0f}k")

ONE_RUN = """
import json, sys
sys.path[:0] = [sys.argv[1], sys.argv[2]]
from export import gridcap_export
from cipt.data import load_request
from cipt.solve import solve
from cipt.trust import plan_digest
print(plan_digest(solve(load_request(gridcap_export("medium")))))
"""
digests = [cipt.trust.plan_digest(base)]
for _ in range(2):
    done = subprocess.run([sys.executable, "-c", ONE_RUN, str(STEPS / "08"), str(Path(__file__).parent)],
                          capture_output=True, text=True, check=True)
    digests.append(done.stdout.strip())
print(f"harness: 3 runs, digests {', '.join(d[:12] for d in digests)}, identical: {len(set(digests)) == 1}")

m = cipt.trust.manifest(raw, cipt.scenario.Scenario("base"), base)
print("manifest: " + json.dumps({**m, "input": m["input"][:12] + "...", "plan": m["plan"][:12] + "..."},
                                sort_keys=True))

demo = json.loads((STEPS / "08" / "data" / "demo.json").read_text())
golden = STEPS / "08" / "tests" / "golden" / "demo_plan.json"
print(f"golden check, code as shipped: {cipt.trust.check_golden(demo, golden) or 'no difference'}")


def starts_cut_one_short(self, project):
    """A planted regression: the window cut ends one year early (years[-1] - duration, no + 1)."""
    return range(max(project.earliest_start, self.years[0]),
                 min(project.latest_start, self.years[-1] - project.duration) + 1)


cipt.data.Request.starts = starts_cut_one_short
print(f"golden check, window cut one year short: {cipt.trust.check_golden(demo, golden)}")
cipt = use(8)

base_2031 = sum(amount for pid, t in base.starts.items()
                for year, amount in request.project(pid).spend(t).items() if year == 2031)
for label, factor in (("cut 10%", 9), ("raised 10%", 11)):
    budget_2031 = raw["budget"]["2031"] * factor // 10
    print(f"2031 {label}: budget ${budget_2031:,}k; the base plan spends ${base_2031:,}k in 2031")
    changed = cipt.data.load_request({**raw, "budget": {**raw["budget"], "2031": budget_2031}})
    for start, previous in (("cold", None), ("warm", base)):
        built = cipt.model.build(changed)
        hint = None if previous is None else {built.x[k]: v for k, v in cipt.solve.hint_values(built, previous).items()}
        result = cipt.solve.run_highs(built.model, hint)
        bound = result.termination.objective_bounds.dual_bound
        print(f"  {start}: {result.termination.reason.name}, NPV ${result.objective_value():,.1f}k, bound ${bound:,.1f}k, "
              f"{result.solve_stats.node_count:,} nodes, {result.solve_stats.simplex_iterations:,} simplex iterations")
