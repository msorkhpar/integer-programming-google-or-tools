from __future__ import annotations

from ortools.math_opt.python import mathopt


def set_objectives(model: mathopt.Model, uncovered, overtime, preferences) -> None:
    """Uncovered shifts first, then overtime, then preferences, as prioritized objectives."""
    model.minimize(uncovered)
    for expr, priority, is_maximize, name in ((overtime, 1, False, "overtime"),
                                              (preferences, 2, True, "preferences")):
        obj = model.add_auxiliary_objective(priority=priority, is_maximize=is_maximize, name=name)
        flat = mathopt.LinearExpression(expr)
        obj.offset = flat.offset
        for var, coefficient in flat.terms.items():
            obj.set_linear_coefficient(var, coefficient)


def build() -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="rota")
    gap = model.add_variable(lb=0, ub=10, name="gap_night")
    extra = model.add_variable(lb=0, ub=40, name="extra_hours")
    likes = [model.add_binary_variable(name=f"likes_{n}") for n in ("ana", "ben", "cy")]
    exprs = {"uncovered": gap, "overtime": 1.5 * extra, "preferences": sum(likes)}
    set_objectives(model, exprs["uncovered"], exprs["overtime"], exprs["preferences"])
    return model, {"gap": gap, "extra": extra, "likes": likes}


if __name__ == "__main__":
    model, _ = build()
    print(model.objective.is_maximize, model.num_auxiliary_objectives())
