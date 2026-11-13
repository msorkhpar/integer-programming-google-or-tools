"""Lesson 6.5.1: what each must-do costs the plan, measured by solving without its row.

GridCap is a fictional utility's portfolio, generated for this course.
"""

from gridcap import generate
from planning_model import build, money, schedule, solve_highs

small = generate("small")
must = [p.project_id for p in small.projects if p.must_do]


def best(relaxed: set[str]) -> tuple[float, dict[str, int]]:
    """The best plan when the must-dos in `relaxed` become discretionary."""
    plan = build(small, must_do=False)
    for i in must:
        if i not in relaxed:
            plan.model.add_linear_constraint(plan.started(i) == 1, name=f"must_{i}")
    result = solve_highs(plan.model)
    return result.objective_value(), schedule(plan, result)


with_all, _ = best(set())
print(f"all must-dos enforced   NPV {money(with_all)}")
for i in must:
    value, starts = best({i})
    kept = "still funded" if i in starts else "dropped"
    print(f"  without must_{i}     NPV {money(value)}  mandate costs {money(value - with_all)}  ({i} {kept})")
value, starts = best(set(must))
print(f"no must-do enforced     NPV {money(value)}  mandates cost {money(value - with_all)}  "
      f"funded anyway: {[i for i in must if i in starts]}")
