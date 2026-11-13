"""Lesson 7.1.4: one optimized GridCap plan, read three ways: by planners, by finance and by a regulator.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from gridcap import REGIONS, generate
from cycle_model import SETTINGS, base_scenario, money, optimize, spend_of

small = generate("small")
scenario = base_scenario(small)
run = optimize(scenario)
funded = {i: small.project(i) for i in run.starts}

print("PLANNERS: what is in, when, and what is out")
late = [f"{i} {p.earliest_start}->{run.starts[i]}" for i, p in funded.items() if run.starts[i] > p.earliest_start]
print(f"  funded {len(funded)} of {len(small.projects)}; {len(late)} start later than they could: {late}")
out = sorted((p for p in small.projects if p.project_id not in funded), key=lambda p: -p.value / p.capex)
print("  not funded, best value per dollar first:")
for p in out[:4]:
    print(f"    {p.project_id} {p.program:12} capex {p.capex:5,}  NPV {p.value:5,}  NPV per $ {p.value / p.capex:.2f}")
print(f"    ... and {len(out) - 4} more")

print("FINANCE: what is spent each year, against what was authorized")
spend = spend_of(small, run.starts)
print("  year  budget   spend  headroom")
for y in small.years:
    print(f"  {y} {small.budget[y]:7,} {spend[y]:7,} {small.budget[y] - spend[y]:9,}")
print(f"  total {sum(small.budget.values()):,} authorized, {sum(spend.values()):,} spent; plan NPV {money(run.npv)}")

print("REGULATOR: are the commitments kept, and can the result be reproduced")
must = [f"{i} in {run.starts.get(i, 'NOT FUNDED')}" for i in small.project_ids if small.project(i).must_do]
print(f"  must-dos: {must}")
for r in REGIONS:
    got = sum(p.capex for p in funded.values() if p.region == r)
    print(f"  {r:6} floor {scenario.floor[r]:6,}  received {got:6,}")
print(f"  status {run.status}, settings {SETTINGS}, input snapshot {run.snapshot[:12]}")
