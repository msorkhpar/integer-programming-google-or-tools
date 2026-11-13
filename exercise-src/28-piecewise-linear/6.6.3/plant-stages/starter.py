from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_stage_order(model: mathopt.Model, built: list[mathopt.Variable], widths: list[float]) -> None:
    """Stage k may begin only when stage k - 1 is finished."""
    # TODO: one binary per stage boundary, and the two rows that tie it to the stages around it.
    return None


def build(widths: list[float]) -> tuple[mathopt.Model, list[mathopt.Variable]]:
    model = mathopt.Model(name="expansion")
    built = [model.add_variable(lb=0, ub=w, name=f"built_{k}") for k, w in enumerate(widths)]
    add_stage_order(model, built, widths)
    model.maximize(sum(built))
    return model, built


if __name__ == "__main__":
    model, built = build([4.0, 3.0, 5.0])
    print(model.get_num_linear_constraints(), "rows")
