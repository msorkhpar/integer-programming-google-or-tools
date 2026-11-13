from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Repair:
    rid: str
    cost: int            # $k
    npv: int             # $k
    risk: int            # safety risk removed, $k a year
    main: str | None = None   # repairs on the same main are alternatives


def select_variables(model: mathopt.Model, repairs: list[Repair]) -> dict[str, mathopt.Variable]:
    """Given: x[rid] = 1 when the repair is funded."""
    return {r.rid: model.add_binary_variable(name=f"x_{r.rid}") for r in repairs}


def add_epsilon_model(model: mathopt.Model, x: dict, repairs: list[Repair], budget: int, risk_floor: int) -> None:
    """The most NPV within the budget, among plans removing at least risk_floor, one repair per main."""
    # TODO: the objective and the rows of your formulation.
    return None


def build(repairs: list[Repair], budget: int, risk_floor: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="leak-repairs")
    x = select_variables(model, repairs)
    add_epsilon_model(model, x, repairs, budget, risk_floor)
    return model, x


if __name__ == "__main__":
    model, x = build([Repair("L1", 40, 30, 10), Repair("L2", 30, 25, 12)], 60, 10)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(result.termination.reason.name, {k: round(result.variable_values(v)) for k, v in x.items()})
