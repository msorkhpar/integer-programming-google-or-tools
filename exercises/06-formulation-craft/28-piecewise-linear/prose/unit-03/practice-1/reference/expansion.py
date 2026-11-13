from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_stage_order(model: mathopt.Model, built: list[mathopt.Variable], widths: list[float]) -> None:
    """Stage k may begin only when stage k - 1 is finished."""
    for k in range(len(widths) - 1):
        done = model.add_binary_variable(name=f"done_{k}")                     # stage k is finished
        model.add_linear_constraint(widths[k] * done <= built[k], name=f"finished_{k}")
        model.add_linear_constraint(built[k + 1] <= widths[k + 1] * done, name=f"may_begin_{k + 1}")


def build(widths: list[float]) -> tuple[mathopt.Model, list[mathopt.Variable]]:
    model = mathopt.Model(name="expansion")
    built = [model.add_variable(lb=0, ub=w, name=f"built_{k}") for k, w in enumerate(widths)]
    add_stage_order(model, built, widths)
    model.maximize(sum(built))
    return model, built


if __name__ == "__main__":
    model, built = build([4.0, 3.0, 5.0])
    print(model.get_num_linear_constraints(), "rows")
