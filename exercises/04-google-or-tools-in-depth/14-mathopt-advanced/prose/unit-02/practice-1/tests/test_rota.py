from rota import build


def coefficients(objective) -> dict[str, float]:
    return {term.variable.name: term.coefficient for term in objective.linear_terms()}


def auxiliary(model) -> dict:
    return {obj.name: obj for obj in model.auxiliary_objectives()}


def test_uncovered_shifts_are_the_primary_objective():
    model, _ = build()
    assert model.objective.is_maximize is False
    assert coefficients(model.objective) == {"gap_night": 1.0}
    assert model.objective.priority == 0


def test_overtime_comes_second_and_is_minimized():
    model, _ = build()
    overtime = auxiliary(model).get("overtime")
    assert overtime is not None and overtime.is_maximize is False
    assert coefficients(overtime) == {"extra_hours": 1.5}
    assert overtime.priority > model.objective.priority


def test_preferences_are_maximized():
    model, _ = build()
    preferences = auxiliary(model).get("preferences")
    assert preferences is not None and preferences.is_maximize is True
    assert coefficients(preferences) == {"likes_ana": 1.0, "likes_ben": 1.0, "likes_cy": 1.0}


def test_preferences_come_after_overtime():
    model, _ = build()
    objs = auxiliary(model)
    assert "overtime" in objs and "preferences" in objs
    assert objs["preferences"].priority > objs["overtime"].priority > model.objective.priority
