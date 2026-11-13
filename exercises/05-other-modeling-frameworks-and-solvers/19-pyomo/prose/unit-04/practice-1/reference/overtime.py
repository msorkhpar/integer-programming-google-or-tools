from __future__ import annotations

import pyomo.environ as pyo


def plan(jobs: dict[str, tuple[float, float]], regular: float,
         hours: list[float], cost: list[float]) -> tuple[float, float, float]:
    """Choose jobs (name -> (hours, value)) to maximize value minus overtime cost.

    Overtime beyond `regular` hours costs the piecewise-linear curve through (hours[k], cost[k]).
    Returns (net value, overtime hours, overtime cost).
    """
    m = pyo.ConcreteModel()
    m.J = pyo.Set(initialize=list(jobs))
    m.x = pyo.Var(m.J, domain=pyo.Binary)
    m.over = pyo.Var(bounds=(hours[0], hours[-1]))
    m.pay = pyo.Var(bounds=(0, None))
    m.time = pyo.Constraint(expr=sum(jobs[j][0] * m.x[j] for j in m.J) <= regular + m.over)
    m.curve = pyo.Piecewise(m.pay, m.over, pw_pts=list(hours), f_rule=list(cost),
                            pw_constr_type="LB", pw_repn="INC")
    m.net = pyo.Objective(expr=sum(jobs[j][1] * m.x[j] for j in m.J) - m.pay, sense=pyo.maximize)
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    solver.solve(m)
    return pyo.value(m.net), m.over.value, m.pay.value


if __name__ == "__main__":
    work = {"A": (30, 900), "B": (20, 500), "C": (25, 400)}
    print(plan(work, 40, [0, 10, 20, 40], [0, 200, 500, 1300]))
