from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Depot:
    name: str
    cap: int        # the most crews it can host
    rate: float     # cost of one crew, $k
    fixed: float    # cost of opening it, $k


def build(depots: list[Depot], low: int, high: int) -> tuple[mathopt.Model, dict, dict]:
    """The crew-staffing model: open[d] binary, crews[d] in {0..cap}, a link row per depot, a band on the total."""
    model = mathopt.Model(name="storm-crews")
    open_ = {d.name: model.add_binary_variable(name=f"open_{d.name}") for d in depots}
    crews = {}
    for d in depots:
        crews[d.name] = model.add_variable(lb=0, ub=d.cap, is_integer=True, name=f"crews_{d.name}")
    for d in depots:
        model.add_linear_constraint(crews[d.name] <= d.cap * open_[d.name], name=f"link_{d.name}")
    model.add_linear_constraint((low <= mathopt.fast_sum(crews.values())) <= high, name="total")
    model.minimize(mathopt.fast_sum(d.rate * crews[d.name] + d.fixed * open_[d.name] for d in depots))
    return model, open_, crews


if __name__ == "__main__":
    depots = [Depot("North", 4, 3.0, 10.0), Depot("South", 3, 2.0, 12.0)]
    model, open_, crews = build(depots, 3, 5)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(result.termination.reason.name, result.objective_value())
