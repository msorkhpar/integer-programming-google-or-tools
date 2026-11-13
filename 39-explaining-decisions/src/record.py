"""One run's record, and the three texts written from it: planners, finance, auditors (lesson 9.3.4).

The record holds only what programs produced: the scenario's inputs and snapshot, the solver's
status, objective and bound, the plan, its diff against the scenario it was copied from, the price
of reversing each changed decision, and the rule checks. The writers read the record and nothing
else, so no number in a text is typed by hand.
"""

from __future__ import annotations

import ortools

from gridcap import Portfolio

from diffs import diff_scenarios, input_changes
from explain_model import SETTINGS, Run, Scenario, build, real_spend, solve
from why import force, rule_facts


def verify(portfolio: Portfolio, scenario: Scenario, plan: dict[str, int]) -> list[tuple[str, bool]]:
    """Check the plan against every rule from the data alone: no model, no solver."""
    by_id = {p.project_id: p for p in portfolio.projects}
    spend = real_spend(portfolio, plan)
    budget = {y: scenario.budget.get(y, portfolio.budget[y]) for y in portfolio.years}
    groups: dict[str, int] = {}
    for pid in plan:
        if by_id[pid].alt_group:
            groups[by_id[pid].alt_group] = groups.get(by_id[pid].alt_group, 0) + 1
    return [
        ("every start is inside its project's window", all(t in by_id[p].starts() for p, t in plan.items())),
        ("every must-do is funded", all(p.project_id in plan for p in portfolio.projects if p.must_do)),
        ("every forced-in project is funded, in its year if one is set",
         all(p in plan and (y is None or plan[p] == y) for p, y in scenario.force_in.items())),
        ("no forced-out project is funded", not (set(plan) & scenario.force_out)),
        ("at most one option per alternative group", all(n <= 1 for n in groups.values())),
        ("every funded child starts its lag after its parent",
         all(by_id[p].parent in plan and t >= plan[by_id[p].parent] + by_id[p].parent_lag
             for p, t in plan.items() if by_id[p].parent)),
        ("each year's spend is within its budget", all(spend[y] <= budget[y] for y in portfolio.years)),
    ]


def make_record(portfolio: Portfolio, parent: Scenario, scenario: Scenario) -> dict:
    """Solve the scenario and its parent, and collect everything the three texts need."""
    before, run = solve(build(portfolio, parent)), solve(build(portfolio, scenario))
    d = diff_scenarios(before, run)
    reasons = {}
    for pid in d.deferred:
        f = force(portfolio, scenario, run, pid)
        reasons[pid] = {"cost_to_reverse": f.cost, "rules": rule_facts(portfolio, run, pid)}
    for pid in d.selected:
        reasons[pid] = {"cost_to_reverse": force(portfolio, scenario, run, pid).cost, "rules": []}
    for pid, old, new in d.shifted:
        reasons[pid] = {"cost_to_reverse": force(portfolio, scenario, run, pid, old).cost, "rules": []}
    again = solve(build(portfolio, scenario))
    return {
        "scenario": scenario.name, "parent": parent.name,
        "snapshot": scenario.snapshot(portfolio), "parent_snapshot": parent.snapshot(portfolio),
        "inputs_changed": input_changes(parent.inputs(portfolio), scenario.inputs(portfolio)),
        "software": {"ortools": ortools.__version__, **SETTINGS},
        "status": run.status, "npv": run.npv, "bound": run.result.best_objective_bound(),
        "parent_npv": before.npv, "funded": len(run.plan), "plan": run.plan,
        "selected": d.selected, "deferred": d.deferred, "shifted": d.shifted, "reasons": reasons,
        "budget": {y: scenario.budget.get(y, portfolio.budget[y]) for y in portfolio.years},
        "spend": real_spend(portfolio, run.plan), "parent_spend": real_spend(portfolio, before.plan),
        "checks": verify(portfolio, scenario, run.plan),
        "rerun_same_plan": again.plan == run.plan,
    }


def in_words(facts: list[dict]) -> str:
    """Rule facts as a planner reads them: the alternative taken, then the budgets with no room."""
    words = [f"its alternative {', '.join(f['funded'])} is in the plan" for f in facts if "funded" in f]
    full = [f"{f['year']} ({f['left']:,} left, needs {f['needs']:,})" for f in facts if "year" in f]
    if full:
        words.append("no room in the budget of " + ", ".join(full))
    return "; ".join(words)


def for_planners(r: dict) -> list[str]:
    lines = [f"Scenario {r['scenario']} funds {r['funded']} projects. Against {r['parent']}:"]
    for pid in r["deferred"]:
        why = in_words(r["reasons"][pid]["rules"])
        lines.append(f"- {pid} leaves the plan ({why}). Putting it back costs ${r['reasons'][pid]['cost_to_reverse']:,}k.")
    for pid in r["selected"]:
        lines.append(f"- {pid} joins the plan. Taking it out again costs ${r['reasons'][pid]['cost_to_reverse']:,}k.")
    for pid, old, new in r["shifted"]:
        word = "earlier" if new < old else "later"
        lines.append(f"- {pid} starts {new} instead of {old} ({word}). Holding it at {old} costs "
                     f"${r['reasons'][pid]['cost_to_reverse']:,}k.")
    cheap = sorted(p for p, v in r["reasons"].items() if v["cost_to_reverse"] < 50)
    lines.append(f"Changes that cost under $50k to reverse are close calls: {', '.join(cheap) or 'none'}.")
    return lines


def for_finance(r: dict) -> list[str]:
    lines = [f"{'year':4}  {'budget':>6}  {'spend':>6}  {'headroom':>8}  {'vs ' + r['parent']:>9}"]
    for y, b in r["budget"].items():
        s = r["spend"][y]
        lines.append(f"{y}  {b:6,}  {s:6,}  {b - s:8,}  {s - r['parent_spend'][y]:+9,}")
    gap = abs(r["bound"] - r["npv"])
    lines.append(f"NPV ${r['npv']:,.0f}k, {r['npv'] - r['parent_npv']:+,.0f}k against {r['parent']} "
                 f"(${r['parent_npv']:,.0f}k); solver status {r['status']}, gap to its bound ${gap:,.0f}k.")
    removed = -sum(r["spend"][y] - r["parent_spend"][y] for y in r["spend"])
    lines.append(f"Spend over the plan falls ${removed:,}k; NPV lost per $k of spend removed: "
                 f"{(r['parent_npv'] - r['npv']) / removed:.3f} (an average over this one change, not a marginal value).")
    return lines


def for_auditors(r: dict) -> list[str]:
    lines = [f"scenario {r['scenario']} snapshot {r['snapshot']}",
             f"copied from {r['parent']} snapshot {r['parent_snapshot']}",
             f"inputs changed: {'; '.join(r['inputs_changed'])}",
             f"software: OR-Tools {r['software']['ortools']}, solver {r['software']['solver']}, "
             f"relative_gap_tolerance {r['software']['relative_gap_tolerance']}",
             f"termination {r['status']}, objective {r['npv']:,.0f}, bound {r['bound']:,.0f}",
             "rules re-checked on the plan from the data, without the model:"]
    lines += [f"  {'PASS' if ok else 'FAIL'}  {rule}" for rule, ok in r["checks"]]
    lines.append(f"rerun of the same snapshot gives the same plan: {r['rerun_same_plan']}")
    return lines
