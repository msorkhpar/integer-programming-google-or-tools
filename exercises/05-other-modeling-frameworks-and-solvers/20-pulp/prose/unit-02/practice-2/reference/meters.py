from __future__ import annotations

from dataclasses import dataclass

import pulp
from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Site:
    sid: str
    district: str
    benefit: float        # $k a year of better readings and fewer truck rolls
    cost: float           # $k
    weeks: int            # installer crew-weeks


def legacy_build(sites, budget, crew_weeks):
    """The inherited PuLP model. Do not change it: the port must give its answers."""
    prob = pulp.LpProblem("meters", pulp.LpMaximize)
    x = pulp.LpVariable.dicts("x", [s.sid for s in sites], cat="Binary")
    k = pulp.LpVariable("extra_crews", 0, 3, cat="Integer")
    prob += pulp.lpSum(s.benefit * x[s.sid] for s in sites) - 40 * k, "net"
    prob += pulp.lpSum(s.cost * x[s.sid] for s in sites) <= budget, "budget"
    prob += pulp.lpSum(s.weeks * x[s.sid] for s in sites) <= crew_weeks + 10 * k, "crew"
    for d in sorted({s.district for s in sites}):
        prob += pulp.lpSum(x[s.sid] for s in sites if s.district == d) >= 1, "cover_" + d
    return prob, x, k


def port_build(sites, budget, crew_weeks):
    """The same model in MathOpt, with the same variable and row names."""
    model = mathopt.Model(name="meters")
    x = {s.sid: model.add_binary_variable(name="x_" + s.sid) for s in sites}
    k = model.add_integer_variable(lb=0, ub=3, name="extra_crews")
    model.maximize(sum(s.benefit * x[s.sid] for s in sites) - 40 * k)
    model.add_linear_constraint(sum(s.cost * x[s.sid] for s in sites) <= budget, name="budget")
    model.add_linear_constraint(sum(s.weeks * x[s.sid] for s in sites) <= crew_weeks + 10 * k, name="crew")
    for d in sorted({s.district for s in sites}):
        model.add_linear_constraint(sum(x[s.sid] for s in sites if s.district == d) >= 1, name="cover_" + d)
    return model, x, k


def port_solve(sites, budget, crew_weeks):
    """(net benefit, sorted site ids, extra crews), solved by SCIP at a gap of 0; None with no plan."""
    model, x, k = port_build(sites, budget, crew_weeks)
    result = mathopt.solve(model, mathopt.SolverType.GSCIP,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    values = result.variable_values()
    return (result.objective_value(), sorted(sid for sid, v in x.items() if values[v] > 0.5),
            round(values[k]))


if __name__ == "__main__":
    demo = [Site("A", "east", 50, 30, 6), Site("B", "west", 40, 30, 8)]
    print(port_solve(demo, budget=100, crew_weeks=10))
