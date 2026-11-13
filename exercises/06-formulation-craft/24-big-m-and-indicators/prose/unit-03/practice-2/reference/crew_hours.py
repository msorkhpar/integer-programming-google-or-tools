from __future__ import annotations

from ortools.sat.python import cp_model


def crew_variables(model: cp_model.CpModel) -> tuple[cp_model.IntVar, cp_model.IntVar]:
    """A crew's hours this week (whole hours, 0 to 60) and whether overtime is approved."""
    hours = model.new_int_var(0, 60, "hours")
    overtime = model.new_bool_var("overtime")
    return hours, overtime


def add_hours_rules(model: cp_model.CpModel, hours: cp_model.IntVar, overtime: cp_model.IntVar) -> None:
    """At most 40 hours without overtime; with overtime, between 45 and 55 hours."""
    model.add(hours <= 40).only_enforce_if(~overtime)
    model.add(hours <= 55).only_enforce_if(overtime)
    model.add(hours >= 45).only_enforce_if(overtime)


if __name__ == "__main__":
    model = cp_model.CpModel()
    hours, overtime = crew_variables(model)
    add_hours_rules(model, hours, overtime)
    model.maximize(hours)
    solver = cp_model.CpSolver()
    solver.solve(model)
    print("most hours:", solver.value(hours))
