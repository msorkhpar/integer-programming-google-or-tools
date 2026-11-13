from __future__ import annotations

from ortools.math_opt.python import mathopt


def verdicts(model: mathopt.Model, x: dict[tuple[str, int], mathopt.Variable], plans: list[dict[str, int]]) -> list[bool]:
    """For each plan (project -> start year), does `model` accept it? Every bound is left as found."""
    found = {key: (var.lower_bound, var.upper_bound) for key, var in x.items()}
    answers = []
    for plan in plans:
        if any((name, year) not in x for name, year in plan.items()):
            answers.append(False)
            continue
        for (name, year), var in x.items():
            var.lower_bound = var.upper_bound = 1.0 if plan.get(name) == year else 0.0
        result = mathopt.solve(model, mathopt.SolverType.HIGHS)
        answers.append(result.termination.reason == mathopt.TerminationReason.OPTIMAL)
    for key, (low, high) in found.items():
        x[key].lower_bound, x[key].upper_bound = low, high
    return answers


if __name__ == "__main__":
    model = mathopt.Model()
    x = {("boiler", 2027): model.add_binary_variable(name="x_boiler_2027")}
    model.add_linear_constraint(x["boiler", 2027] == 1, name="must_boiler")
    print(verdicts(model, x, [{"boiler": 2027}, {}]))
