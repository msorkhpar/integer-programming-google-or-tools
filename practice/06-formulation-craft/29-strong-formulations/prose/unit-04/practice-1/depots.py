from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Depots:
    demand: dict             # substation -> spare parts it draws per year
    capacity: dict           # depot -> spare parts it can hold
    fee: dict                # depot -> yearly cost of keeping it open ($k)
    haul: dict               # (substation, depot) -> yearly hauling cost ($k)


def add_inherited_rules(model, x, y, d: Depots) -> None:
    """The colleague's rows: correct for whole plans, weak for the LP."""
    subs, depots = list(d.demand), list(d.capacity)
    for j in depots:
        model.add_linear_constraint(sum(x[i, j] for i in subs) <= len(subs) * y[j], name=f"open_{j}")
        model.add_linear_constraint(sum(d.demand[i] * x[i, j] for i in subs) <= d.capacity[j], name=f"cap_{j}")


def add_rules(model, x, y, d: Depots) -> None:
    """The same rules, reformulated: as strong as you can make them."""
    # TODO: the open and capacity rules, in their strongest form.
    return None

def build(d: Depots, rules, *, integer: bool = True) -> tuple[mathopt.Model, dict, dict]:
    """Serve every substation from one open depot at the least yearly cost."""
    model = mathopt.Model(name="depots")
    x = {(i, j): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}_{j}")
         for i in d.demand for j in d.capacity}
    y = {j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"y_{j}") for j in d.capacity}
    for i in d.demand:
        model.add_linear_constraint(sum(x[i, j] for j in d.capacity) == 1, name=f"served_{i}")
    rules(model, x, y, d)
    model.minimize(sum(d.fee[j] * y[j] for j in d.capacity) + sum(d.haul[k] * x[k] for k in x))
    return model, x, y


if __name__ == "__main__":
    d = Depots({"S1": 4, "S2": 3}, {"D1": 8, "D2": 8}, {"D1": 10, "D2": 12},
               {("S1", "D1"): 1, ("S1", "D2"): 2, ("S2", "D1"): 2, ("S2", "D2"): 1})
    for rules in (add_inherited_rules, add_rules):
        model, _, _ = build(d, rules, integer=False)
        print(rules.__name__, mathopt.solve(model, mathopt.SolverType.GLOP).objective_value())
