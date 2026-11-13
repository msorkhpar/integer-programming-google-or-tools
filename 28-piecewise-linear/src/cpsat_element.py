"""Lesson 6.6.4: the renewal fund with depths in quarter steps, in CP-SAT with `add_element` and in MathOpt.

GridCap is a fictional utility's portfolio. CP-SAT has no SOS2 and no piecewise-linear constraint,
and works on integers. When the decision itself takes a few integer values (here a depth of 0, 1, 2,
3 or 4 quarters), the curve is a table, and `add_element(index, values, target)` says
target = values[index]. Values are rounded to whole $k so both solvers see the same numbers.
"""

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import generate
from lifecycle import candidates, value_curve
from piecewise import Curve, add_incremental, value
from renewal_plan import FUND
from selection import EXACT, solve_highs


def table(asset) -> list[int]:
    return [round(v) for v in value_curve(asset).ys]


def cpsat(portfolio):
    model = cp_model.CpModel()
    quarters, worth = {}, {}
    for p, a in candidates(portfolio):
        quarters[p.project_id] = model.new_int_var(0, 4, f"q_{p.project_id}")
        worth[p.project_id] = model.new_int_var(0, max(table(a)), f"v_{p.project_id}")
        model.add_element(quarters[p.project_id], table(a), worth[p.project_id])
    model.add(sum(p.capex * quarters[p.project_id] for p, _ in candidates(portfolio)) <= 4 * FUND)
    model.maximize(sum(worth.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    status = solver.solve(model)
    return solver.status_name(status), solver.objective_value, {i: solver.value(q) for i, q in quarters.items()}


def mathopt_quarters(portfolio):
    model = mathopt.Model()
    quarters, worth = {}, []
    for p, a in candidates(portfolio):
        piece = add_incremental(model, Curve((0.0, 0.25, 0.5, 0.75, 1.0), tuple(table(a))), p.project_id)
        quarters[p.project_id] = model.add_integer_variable(lb=0, ub=4, name=f"q_{p.project_id}")
        model.add_linear_constraint(piece.x == quarters[p.project_id] / 4)
        worth.append(piece.y)
    model.add_linear_constraint(sum(p.capex * quarters[p.project_id] / 4 for p, _ in candidates(portfolio)) <= FUND)
    model.maximize(sum(worth))
    result = solve_highs(model, EXACT)
    return result.objective_value(), {i: round(value(result, q)) for i, q in quarters.items()}


if __name__ == "__main__":
    small = generate("small")
    status, best, q = cpsat(small)
    print(f"CP-SAT, add_element : {status}, ${best:,.0f}k, quarters {({i: v for i, v in q.items() if v})}")
    best, q = mathopt_quarters(small)
    print(f"MathOpt, incremental: OPTIMAL, ${best:,.0f}k, quarters {({i: v for i, v in q.items() if v})}")
