"""Diff GridCap's base scenario against a copy with a smaller 2029 budget (lesson 9.3.3)."""

from gridcap import generate

from diffs import diff_scenarios, input_changes, show
from explain_model import Scenario, build, solve

small = generate("small")
base = Scenario("base")
cut = Scenario("cut-2029", budget={2029: 6000})
a, b = solve(build(small, base)), solve(build(small, cut))
print(f"{base.name}: {a.status} NPV ${a.npv:,.0f}k, {len(a.plan)} funded, snapshot {base.snapshot(small)[:12]}")
print(f"{cut.name}: {b.status} NPV ${b.npv:,.0f}k, {len(b.plan)} funded, snapshot {cut.snapshot(small)[:12]}")
print()
print("inputs changed:")
for line in input_changes(base.inputs(small), cut.inputs(small)):
    print(f"  {line}")
print("plan changed:")
for line in show(diff_scenarios(a, b)):
    print(f"  {line}")
