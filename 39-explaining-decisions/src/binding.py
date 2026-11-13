"""A binding-constraints report for a solved GridCap plan (lesson 9.3.1).

Two questions, both answered from the plan and the rows, with no dual values:
- which rows have no slack left (`slack_table`);
- which rows refuse each single project the plan could add (`refusals`).
"""

from __future__ import annotations

from explain_model import TOL, Built, family, plan_values, slack


def slack_table(built: Built, plan: dict[str, int]) -> list[tuple[str, str, float]]:
    """(row name, rule family, slack) for every row, slack measured on the plan."""
    values = plan_values(built, plan)
    return [(name, family(name), slack(row, values)) for name, row in built.rows.items()]


def refusals(built: Built, plan: dict[str, int]) -> dict[tuple[str, int], list[str]]:
    """For every project the plan leaves out and every start year it allows: the rows that adding it breaks."""
    out = {}
    for p in built.portfolio.projects:
        if p.project_id in plan:
            continue
        for t in p.starts():
            values = plan_values(built, {**plan, p.project_id: t})
            out[p.project_id, t] = [name for name, row in built.rows.items() if slack(row, values) < -TOL]
    return out
