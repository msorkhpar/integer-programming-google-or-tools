from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Pipe:
    pid: str
    kg_per_mm: float    # resin per mm of liner thickness
    min_mm: float       # structural minimum thickness if relined


def add_liner_rules(model: mathopt.Model, x: dict, t: mathopt.Variable, pipes: list[Pipe],
                    t_low: float, t_high: float, supply: float) -> None:
    """Resin at the program's thickness for every relined pipe within supply; each relined pipe's minimum."""
    resin = []
    for p in pipes:
        lined = model.add_variable(lb=0, ub=t_high, name=f"lined_{p.pid}")    # x[p] * t
        model.add_linear_constraint(lined <= t_high * x[p.pid], name=f"lined_off_{p.pid}")
        model.add_linear_constraint(lined <= t - t_low * (1 - x[p.pid]), name=f"lined_le_{p.pid}")
        model.add_linear_constraint(lined >= t_low * x[p.pid], name=f"lined_on_{p.pid}")
        model.add_linear_constraint(lined >= t - t_high * (1 - x[p.pid]), name=f"lined_ge_{p.pid}")
        model.add_linear_constraint(t >= p.min_mm * x[p.pid], name=f"thick_{p.pid}")
        resin.append(p.kg_per_mm * lined)
    model.add_linear_constraint(sum(resin) <= supply, name="supply")


def build(pipes: list[Pipe], t_low: float, t_high: float, supply: float) -> tuple[mathopt.Model, dict, mathopt.Variable]:
    model = mathopt.Model(name="relining")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in pipes}
    t = model.add_variable(lb=t_low, ub=t_high, name="t")
    add_liner_rules(model, x, t, pipes, t_low, t_high, supply)
    model.maximize(sum(x.values()))
    return model, x, t


if __name__ == "__main__":
    pipes = [Pipe("Main St", 10.0, 4.0), Pipe("Mill Rd", 8.0, 6.0)]
    model, x, t = build(pipes, 3.0, 8.0, 100.0)
    print(len(list(model.linear_constraints())), "rows")
