from ortools.math_opt.python import mathopt

from verdict import verdicts

# The hospital's projects: the years each may start in, and what it costs in its start year ($k).
WINDOWS = {"mri": (2027, 2028), "boiler": (2027,), "pump": (2027,), "lift": (2028,)}
COST = {"mri": 70, "boiler": 40, "pump": 25, "lift": 30}
BUDGET = 80          # each year, $k
OVERTIME = 30        # at most this much more each year, paid as overtime


def hospital():
    """A fresh model: once rows, the boiler as a must-do, and a budget row per year with overtime."""
    model = mathopt.Model()
    x = {(name, t): model.add_binary_variable(name=f"x_{name}_{t}") for name, years in WINDOWS.items() for t in years}
    for name, years in WINDOWS.items():
        model.add_linear_constraint(sum(x[name, t] for t in years) <= 1, name=f"once_{name}")
    model.add_linear_constraint(x["boiler", 2027] == 1, name="must_boiler")
    for t in (2027, 2028):
        overtime = model.add_variable(lb=0, ub=OVERTIME, name=f"overtime_{t}")
        model.add_linear_constraint(
            sum(COST[name] * x[name, t] for name, years in WINDOWS.items() if t in years) <= BUDGET + overtime,
            name=f"budget_{t}")
    return model, x


def ask(*plans):
    model, x = hospital()
    return verdicts(model, x, list(plans))


def test_a_plan_within_the_money_is_allowed_and_one_over_it_refused():
    assert ask({"boiler": 2027, "lift": 2028}, {"boiler": 2027, "mri": 2027, "pump": 2027}) == [True, False]


def test_a_plan_without_the_must_do_is_refused():
    assert ask({"boiler": 2027, "lift": 2028}, {"lift": 2028}) == [True, False]


def test_overtime_stays_the_models_to_choose():
    assert ask({"boiler": 2027, "mri": 2027}, {"boiler": 2027, "mri": 2027, "pump": 2027}) == [True, False]


def test_a_start_outside_the_window_is_refused():
    assert ask({"boiler": 2027, "lift": 2028}, {"boiler": 2027, "lift": 2027}) == [True, False]


def test_the_model_is_left_as_it_was_found():
    model, x = hospital()
    x["mri", 2028].lower_bound = 1.0          # a planner's override: the MRI starts in 2028
    before = {key: (var.lower_bound, var.upper_bound) for key, var in x.items()}
    assert verdicts(model, x, [{"boiler": 2027, "lift": 2028}, {"lift": 2028}]) == [True, False]
    assert {key: (var.lower_bound, var.upper_bound) for key, var in x.items()} == before
