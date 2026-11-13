"""Ridge's crew split with jobs counted by length: fewer variables, fewer copies of each plan."""

from gridcap import generate
from crew_split import build, build_counts, params, region_jobs
from strong_model import size, solve_highs

jobs = region_jobs(generate("medium"), "Ridge")
lengths = sorted(set(jobs.values()), reverse=True)
print("job lengths and how many of each:", {s: list(jobs.values()).count(s) for s in lengths})
for name, model in (("named jobs", build(jobs, 4).model), ("counted jobs", build_counts(jobs, 4).model),
                    ("counted jobs, load order", build_counts(jobs, 4, "load").model)):
    for detect in (False, True):
        result = solve_highs(model, params(detect))
        variables, rows = size(model)
        print(f"{name:24}  variables {variables:2}  rows {rows:2}  detection {'on' if detect else 'off':3}  "
              f"makespan {result.objective_value():.0f}  nodes {result.solve_stats.node_count}")
