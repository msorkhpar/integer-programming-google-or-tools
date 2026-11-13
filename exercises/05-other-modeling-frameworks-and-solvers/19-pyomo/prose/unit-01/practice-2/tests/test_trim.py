import pytest

from trim import Circuit, trim_plan

# A distribution company's feeder lines, not the lesson's portfolio.
SPRING = {"F1": Circuit(60, 9.0, ("Apr", "May")), "F2": Circuit(50, 7.0, ("Apr",)),
          "F3": Circuit(40, 4.0, ("May", "Jun")), "F4": Circuit(30, 3.5, ("Apr", "Jun")),
          "F5": Circuit(70, 8.0, ("May",))}
HOURS = {"Apr": 100, "May": 90, "Jun": 40}


def check(circuits, hours, plan):
    for c, month in plan.items():
        assert month in circuits[c].months, f"{c} is trimmed in {month}, outside its window"
    for month, cap in hours.items():
        used = sum(circuits[c].hours for c, k in plan.items() if k == month)
        assert used <= cap, f"{month} uses {used} crew hours, more than {cap}"


def solve(circuits, hours):
    try:
        return trim_plan(circuits, hours)
    except Exception as error:      # a model that cannot be built is a wrong answer here
        raise AssertionError(f"trim_plan raised {type(error).__name__}: {error}") from None


def test_the_plan_removes_the_most_risk_within_windows_and_hours():
    value, plan = solve(SPRING, HOURS)
    assert value == pytest.approx(24.5)
    check(SPRING, HOURS, plan)
    assert sum(SPRING[c].risk for c in plan) == pytest.approx(value)


def test_tighter_crews_change_the_plan():
    hours = {"Apr": 60, "May": 70, "Jun": 40}
    value, plan = solve(SPRING, hours)
    assert value == pytest.approx(21.0)
    check(SPRING, hours, plan)


def test_a_month_no_circuit_may_use_and_a_circuit_with_no_month():
    circuits = dict(SPRING, F6=Circuit(20, 5.0, ()))
    hours = dict(HOURS, Jul=50)
    value, plan = solve(circuits, hours)
    assert value == pytest.approx(24.5)
    assert "F6" not in plan


def test_a_month_missing_from_crew_hours_has_no_crews():
    circuits = dict(SPRING, F7=Circuit(10, 50.0, ("Aug",)), F8=Circuit(30, 6.0, ("Aug", "Jun")))
    value, plan = solve(circuits, HOURS)
    assert value == pytest.approx(26.5)
    assert "F7" not in plan, "F7's only month, Aug, has no crew hours"
    assert plan.get("F8") in (None, "Jun"), "F8 may only be trimmed in Jun, the month of its two that has crews"
    check(circuits, HOURS, plan)
    assert value == pytest.approx(sum(circuits[c].risk for c in plan))
