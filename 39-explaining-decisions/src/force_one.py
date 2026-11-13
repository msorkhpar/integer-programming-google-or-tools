"""Price one decision by forcing the opposite and re-solving (lesson 9.3.2)."""

from gridcap import generate

from explain_model import Scenario, build, solve
from why import changes, force, rules_against

small = generate("small")
scenario = Scenario()
base = solve(build(small, scenario))
print(f"base: NPV ${base.npv:,.0f}k, {len(base.plan)} funded")
print()

for pid in ("P024", "P032", "P002"):
    forced = force(small, scenario, base, pid)
    added, dropped, moved = changes(base.plan, forced.plan)
    print(f"force {pid} {forced.action}: {forced.status}, NPV ${base.npv - forced.cost:,.0f}k, "
          f"cost ${forced.cost:,}k (its own NPV at its best start: ${max(small.project(pid).npv.values()):,}k)")
    print(f"  added {added}  dropped {dropped}")
    print(f"  moved {moved}")
    if forced.action == "in":
        for rule in rules_against(small, base, pid):
            print(f"  as the plan stands: {rule}")
    print()

for pid in ("P017", "P039"):
    forced = force(small, scenario, base, pid)
    rows = sorted(name for name in build(small, Scenario(force_out=frozenset({pid}))).rows if name.endswith(pid))
    print(f"force {pid} {forced.action}: {forced.status}; its rows {rows}")
