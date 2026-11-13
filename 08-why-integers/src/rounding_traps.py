"""Two invented four-line models where rounding fails badly. Not GridCap data."""

from ortools.math_opt.python import mathopt

from selection import solve_highs


def knapsack(costs: dict, values: dict, budget: int, integer: bool) -> mathopt.SolveResult:
    model = mathopt.Model(name="trap")
    x = {k: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{k}") for k in costs}
    model.add_linear_constraint(sum(costs[k] * x[k] for k in costs) <= budget, name="budget")
    model.maximize(sum(values[k] * x[k] for k in costs))
    result = mathopt.solve(model, mathopt.SolverType.GLOP) if not integer else solve_highs(model)
    return result, x


def cover(costs: dict, km: dict, need: int) -> mathopt.SolveResult:
    """Clear at least `need` km of corridor at least cost: a >= row."""
    model = mathopt.Model(name="cover")
    x = {k: model.add_variable(lb=0, ub=1, name=f"x_{k}") for k in costs}
    model.add_linear_constraint(sum(km[k] * x[k] for k in costs) >= need, name="clear")
    model.minimize(sum(costs[k] * x[k] for k in costs))
    return mathopt.solve(model, mathopt.SolverType.GLOP), x


if __name__ == "__main__":
    costs, values = {"A": 1, "B": 100}, {"A": 2, "B": 100}
    lp, x = knapsack(costs, values, 100, integer=False)
    print("trap 1: A costs 1 and is worth 2, B costs 100 and is worth 100, budget 100")
    print(f"  LP: x_A = {lp.variable_values(x['A']):.2f}, x_B = {lp.variable_values(x['B']):.2f}, "
          f"value {lp.objective_value():.2f}")
    down = [k for k in costs if lp.variable_values(x[k]) > 1 - 1e-6]
    print(f"  round down: {down}, value {sum(values[k] for k in down)}")
    ip, y = knapsack(costs, values, 100, integer=True)
    print(f"  optimum: {[k for k in costs if ip.variable_values(y[k]) > 0.5]}, value {ip.objective_value():.0f}")

    costs, km = {"C": 300, "D": 500, "E": 450}, {"C": 200, "D": 300, "E": 250}
    lp, x = cover(costs, km, 400)
    print("trap 2: clear at least 400 km; C clears 200 km for 300, D 300 km for 500, E 250 km for 450")
    print("  LP: " + ", ".join(f"x_{k} = {lp.variable_values(x[k]):.2f}" for k in costs))
    down = [k for k in costs if lp.variable_values(x[k]) > 1 - 1e-6]
    print(f"  round down: {down}, clears {sum(km[k] for k in down)} km of the 400 required")
