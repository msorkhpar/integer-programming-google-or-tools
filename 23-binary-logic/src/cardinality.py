"""Lesson 6.1.3: at most k, at least k and exactly k, each one row on a count, on GridCap small.

GridCap is a fictional utility's portfolio, and the three rules are invented for the lesson.
"""

from gridcap import REGIONS, generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")


def count(sel, members):
    return sum(sel.x[i] for i in members)


def at_most(sel):         # the Valley transmission yard can stage at most 2 projects
    sel.model.add_linear_constraint(count(sel, ids(small, program="transmission", region="Valley")) <= 2,
                                    name="valley_yard")


def at_least(sel):        # the rate case promises every region at least 4 projects
    for r in REGIONS:
        sel.model.add_linear_constraint(count(sel, ids(small, region=r)) >= 4, name=f"promise_{r}")


def exactly(sel):         # the Coast vegetation crew is contracted for exactly 2 jobs
    sel.model.add_linear_constraint(count(sel, ids(small, program="vegetation", region="Coast")) == 2,
                                    name="coast_crew")


def report(rule, groups):
    sel = build(small)
    if rule:
        rule(sel)
    result = solve_highs(sel.model, EXACT)
    plan = funded(sel, result)
    counts = ", ".join(f"{label} {sum(i in plan for i in members)}" for label, members in groups.items())
    print(f"{rule.__name__ if rule else 'no rule':8} NPV ${result.objective_value():,.0f}k  {counts}")


groups = {"Valley transmission": ids(small, program="transmission", region="Valley"),
          **{r: ids(small, region=r) for r in REGIONS},
          "Coast vegetation": ids(small, program="vegetation", region="Coast")}
for rule in (None, at_most, at_least, exactly):
    report(rule, groups)
