"""One GridCap small project's cost profile, and the s_{i,y} entries the yearly budget rows take from it."""

from gridcap import generate

small = generate("small")
years = range(2027, 2032)
p = next(p for p in small.projects if p.earliest_start > 2027 and len(p.cost_profile) >= 3)
print(f"{p.project_id}: earliest start e = {p.earliest_start}, cost profile {list(p.cost_profile)} ($k by year of work)")
spend = p.spend(p.earliest_start)
for y in years:
    k = y - p.earliest_start
    entry = f"profile[{k}]" if y in spend else "not worked"
    print(f"  s[{p.project_id},{y}] = {spend.get(y, 0):5,}   {entry}")
