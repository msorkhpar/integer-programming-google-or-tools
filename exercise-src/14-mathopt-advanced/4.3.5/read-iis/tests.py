from ortools.math_opt.python import mathopt

from explain import explain

B = mathopt.ModelSubsetBounds
INFEASIBLE, FEASIBLE = mathopt.FeasibilityStatus.INFEASIBLE, mathopt.FeasibilityStatus.FEASIBLE


def freight():
    """A rail freight plan, not the lesson's portfolio."""
    model = mathopt.Model()
    cars = model.add_integer_variable(lb=0, ub=40, name="cars")
    crew = model.add_variable(lb=2, ub=6, name="crew")
    rows = {
        "track_cap": model.add_linear_constraint(cars + crew <= 30, name="track_cap"),
        "yard_cap": model.add_linear_constraint(cars <= 25, name="yard_cap"),
        "orders": model.add_linear_constraint(cars == 32, name="orders"),
    }
    return model, cars, crew, rows


def result(feasibility=INFEASIBLE, rows=None, bounds=None, integer=frozenset()):
    subset = mathopt.ModelSubset(linear_constraints=rows or {}, variable_bounds=bounds or {},
                                 variable_integrality=frozenset(integer))
    return mathopt.ComputeInfeasibleSubsystemResult(feasibility=feasibility, infeasible_subsystem=subset,
                                                    is_minimal=True)


def test_upper_sides_of_rows_are_listed():
    _, _, _, rows = freight()
    r = result(rows={rows["yard_cap"]: B(upper=True), rows["track_cap"]: B(upper=True)})
    assert explain(r) == ["track_cap <= 30", "yard_cap <= 25"]


def test_only_an_infeasible_result_explains_anything():
    _, _, _, rows = freight()
    subset = {rows["yard_cap"]: B(upper=True)}
    assert explain(result(FEASIBLE, rows=subset)) == []
    assert explain(result(INFEASIBLE, rows=subset)) == ["yard_cap <= 25"]


def test_only_the_sides_in_the_subsystem_are_listed():
    _, _, _, rows = freight()
    r = result(rows={rows["orders"]: B(lower=True), rows["yard_cap"]: B(upper=True)})
    assert explain(r) == ["orders >= 32", "yard_cap <= 25"]


def test_variable_bounds_and_integrality_are_listed():
    _, cars, crew, rows = freight()
    r = result(rows={rows["track_cap"]: B(upper=True)}, bounds={crew: B(lower=True)}, integer={cars})
    assert explain(r) == ["cars is integer", "crew >= 2", "track_cap <= 30"]
