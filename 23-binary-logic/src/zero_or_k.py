"""Lesson 6.1.3: "none, or at least k" needs a switch variable per group.

GridCap is a fictional utility's portfolio. The invented rule: the vegetation contractor only goes
to a region if it gets at least 2 vegetation jobs there.
"""

from gridcap import REGIONS, generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")
K = 2
vegetation = {r: ids(small, program="vegetation", region=r) for r in REGIONS}


def solve(rule: bool):
    sel = build(small)
    model, x = sel.model, sel.x
    go = {}
    if rule:
        for r, members in vegetation.items():
            go[r] = model.add_binary_variable(name=f"go_{r}")
            jobs = sum(x[i] for i in members)
            model.add_linear_constraint(jobs >= K * go[r], name=f"enough_{r}")
            model.add_linear_constraint(jobs <= len(members) * go[r], name=f"only_if_{r}")
    result = solve_highs(model, EXACT)
    plan = funded(sel, result)
    jobs = {r: [i for i in members if i in plan] for r, members in vegetation.items()}
    sent = {r: round(result.variable_values(v)) for r, v in go.items()}
    return result.objective_value(), jobs, sent


for rule in (False, True):
    npv, jobs, sent = solve(rule)
    print(f"{'with' if rule else 'without'} the rule: NPV ${npv:,.0f}k")
    for r in REGIONS:
        note = f"  go={sent[r]}" if sent else ""
        n = len(vegetation[r])
        print(f"  {r:6} {n} candidate{'s' if n != 1 else ' '}, funded {jobs[r]}{note}")
