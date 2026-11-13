"""Lesson 14.2.2: what the one-envelope plan spends each year, and the plan with yearly budgets.

GridCap small is a fictional utility's portfolio. The step-01 plan starts every project in its
earliest year; its yearly spend is computed here from the export's cost profiles and compared with
the yearly budgets the export also carries. Then steps/02 plans with those budgets.
"""

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
budget = {int(y): v for y, v in raw["budget"].items()}
profile = {r["id"]: r["cost_profile"] for r in raw["projects"]}


def spend(starts: dict[str, int]) -> dict[int, int]:
    out = {y: 0 for y in budget}
    for pid, start in starts.items():
        for k, amount in enumerate(profile[pid]):
            out[start + k] = out.get(start + k, 0) + amount
    return out


old = use(1)
first = old.solve.solve(old.data.load_request(raw))
print("step 01 plan, spend against each year's budget ($k):")
for year, amount in spend(first.starts).items():
    flag = f"  over by {amount - budget[year]:,}" if amount > budget[year] else ""
    print(f"  {year}  {amount:>6,} of {budget[year]:>6,}{flag}")

new = use(2)
request = new.data.load_request(raw)
built = new.model.build(request)
print(f"step 02 model: {len(built.x)} binary variables, {len(built.rows)} rows")
plan = new.solve.solve(request)
print("\n".join(new.report.render(request, plan).splitlines()[:7]))
late = sorted(pid for pid, t in plan.starts.items() if t > request.project(pid).earliest_start)
print(f"started after their earliest year: {len(late)} of {len(plan.starts)} ({', '.join(late)})")
