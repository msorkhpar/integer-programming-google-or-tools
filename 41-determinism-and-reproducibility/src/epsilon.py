"""Lesson 10.2.3: one solve, most projects first and NPV second, through a small weight epsilon.

The objective is count + eps * NPV. With eps too large the NPV term outweighs a whole project; with
eps too small it falls under the solver's tolerances and is ignored. GridCap is fictional.
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, digest, schedule, solve_highs

small = generate("small")
most_npv = sum(max(p.npv.values()) for p in small.projects)     # no plan's NPV can exceed this
print(f"largest NPV any plan could have: {most_npv:,}  -> safe eps below 1/{most_npv + 1:,}")

for label, eps in [("1e-3", 1e-3), (f"1/{most_npv + 1:,}", 1 / (most_npv + 1)), ("1e-9", 1e-9)]:
    plan = build(small, objective="count")
    npv = sum(small.project(i).npv[t] * v for (i, t), v in plan.x.items())
    plan.model.maximize(sum(plan.x.values()) + eps * npv)
    starts = schedule(plan, solve_highs(plan.model, mathopt.SolveParameters(relative_gap_tolerance=0.0)))
    value = sum(small.project(i).npv[t] for i, t in starts.items())
    print(f"eps {label:<9} projects {len(starts)}  NPV {value:,}  plan {digest(starts)}")
