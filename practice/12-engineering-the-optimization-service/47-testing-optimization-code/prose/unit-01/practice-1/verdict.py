from __future__ import annotations

from ortools.math_opt.python import mathopt


def verdicts(model: mathopt.Model, x: dict[tuple[str, int], mathopt.Variable], plans: list[dict[str, int]]) -> list[bool]:
    """For each plan (project -> start year), does `model` accept it? Every bound is left as found."""
    # TODO: fix each plan into the model, solve, read the answer, and leave the model as found.
    return [True for plan in plans]

if __name__ == "__main__":
    model = mathopt.Model()
    x = {("boiler", 2027): model.add_binary_variable(name="x_boiler_2027")}
    model.add_linear_constraint(x["boiler", 2027] == 1, name="must_boiler")
    print(verdicts(model, x, [{"boiler": 2027}, {}]))
