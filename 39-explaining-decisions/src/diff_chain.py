"""Two changes made one at a time, in both orders: what each step is charged depends on the order (lesson 9.3.3)."""

from gridcap import generate

from diffs import diff_scenarios
from explain_model import Scenario, build, solve

small = generate("small")
cut = {2029: 6000}
scenarios = {
    "base": Scenario("base"),
    "cut": Scenario("cut", budget=cut),
    "P024": Scenario("P024", force_in={"P024": None}),
    "cut+P024": Scenario("cut+P024", budget=cut, force_in={"P024": None}),
}
runs = {name: solve(build(small, s)) for name, s in scenarios.items()}

for path in (("base", "cut", "cut+P024"), ("base", "P024", "cut+P024")):
    print(" -> ".join(path))
    for a, b in zip(path, path[1:]):
        d = diff_scenarios(runs[a], runs[b])
        print(f"  {a:>4} -> {b:8}  NPV {d.npv:+6,.0f}  selected {d.selected}  deferred {d.deferred}  shifted {len(d.shifted)}")
    total = diff_scenarios(runs[path[0]], runs[path[-1]])
    print(f"  whole path      NPV {total.npv:+6,.0f}  selected {total.selected}  deferred {total.deferred}  shifted {len(total.shifted)}")
