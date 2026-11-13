"""Lesson 5.2.2: a GridCap selection script in the style of older PuLP code, to be read and ported.

The model is the one-period selection of lesson 1.1.1: fund projects to maximize value within one
capital budget, with must-do, parent and alternative-group rules. GridCap is a fictional utility's
portfolio. The style (variables made apart from the problem, the status read through a dict, the
bundled CBC) is how PuLP code written before 3.3 looks.
"""

from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpStatus, LpVariable, lpSum, value


def solve_legacy(portfolio, gap=None):
    """Return (status text, value, funded project ids, problem)."""
    ids = [p.project_id for p in portfolio.projects]
    x = LpVariable.dicts("x", ids, cat="Binary")

    prob = LpProblem("selection", LpMaximize)
    prob += lpSum(p.value * x[p.project_id] for p in portfolio.projects)

    prob += lpSum(p.capex * x[p.project_id] for p in portfolio.projects) <= portfolio.capital_budget, "budget"
    for p in portfolio.projects:
        if p.must_do:
            prob += x[p.project_id] == 1, "must_" + p.project_id
        if p.parent:
            prob += x[p.project_id] <= x[p.parent], "parent_" + p.project_id

    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(x[p.project_id])
    for g in groups:
        prob += lpSum(groups[g]) <= 1, "alt_" + g

    prob.solve(PULP_CBC_CMD(msg=0, gapRel=gap))
    status = LpStatus[prob.status]
    funded = [i for i in ids if value(x[i]) > 0.5]
    return status, value(prob.objective), funded, prob
