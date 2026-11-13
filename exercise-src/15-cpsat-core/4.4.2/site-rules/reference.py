from __future__ import annotations

from ortools.sat.python import cp_model


def site_variables(model: cp_model.CpModel) -> dict:
    """The warehouse's decisions for one day."""
    return {
        "night": model.new_bool_var("night"),            # the night shift runs
        "freezer": model.new_bool_var("freezer"),        # the freezer room is open
        "dock_a": model.new_bool_var("dock_a"),          # dock A is open
        "dock_b": model.new_bool_var("dock_b"),          # dock B is open
        "night_staff": model.new_int_var(0, 20, "night_staff"),
        "frozen_orders": model.new_int_var(0, 500, "frozen_orders"),
        "forklifts": model.new_int_var(0, 6, "forklifts"),
    }


def add_site_rules(model: cp_model.CpModel, v: dict, min_night: int, forklifts_both: int) -> None:
    """The site rules, each a linear row switched by literals."""
    model.add(v["night_staff"] >= min_night).only_enforce_if(v["night"])
    model.add(v["night_staff"] == 0).only_enforce_if(~v["night"])
    model.add(v["frozen_orders"] == 0).only_enforce_if(~v["freezer"])
    model.add(v["forklifts"] >= forklifts_both).only_enforce_if(v["dock_a"], v["dock_b"])


if __name__ == "__main__":
    model = cp_model.CpModel()
    v = site_variables(model)
    add_site_rules(model, v, 4, 3)
    model.maximize(v["frozen_orders"] - 10 * v["forklifts"])
    solver = cp_model.CpSolver()
    print(solver.status_name(solver.solve(model)), {k: solver.value(x) for k, x in v.items()})
