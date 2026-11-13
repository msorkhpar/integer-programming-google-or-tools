from pydantic import ValidationError

from trim_result import TrimResult

GOOD = {"status": "optimal", "message": "Best trim plan found and proven.", "value": 240.0, "bound": 240.0,
        "gap": 0.0, "circuits": ["C-2", "C-7"],
        "hours_by_month": [{"month": 3, "crew_hours": 120, "capacity": 160},
                           {"month": 4, "crew_hours": 160, "capacity": 160}]}
NONE = {"status": "infeasible", "message": "No plan meets every rule.", "value": None, "bound": None,
        "gap": None, "circuits": [], "hours_by_month": []}


def accepted(base=GOOD, **changes) -> bool:
    try:
        TrimResult(**{**base, **changes})
        return True
    except ValidationError:
        return False


def test_a_consistent_result_is_accepted_and_an_unknown_status_refused():
    assert accepted() and accepted(NONE)
    assert not accepted(status="done")


def test_an_optimal_result_carries_its_value():
    assert accepted(value=0.0, bound=0.0)
    assert not accepted(value=None, gap=None)


def test_an_infeasible_result_has_no_plan():
    assert accepted(NONE)
    assert not accepted(NONE, circuits=["C-2"])


def test_a_failed_result_has_no_value():
    assert accepted(NONE, status="failed")
    assert not accepted(NONE, status="failed", value=10.0)


def test_gap_comes_with_value_and_bound():
    assert accepted(status="time_limit", bound=300.0, gap=0.25)
    assert not accepted(status="time_limit", bound=None, gap=0.25)


def test_a_negative_gap_is_refused():
    assert accepted(gap=0.0)
    assert not accepted(gap=-0.01)


def test_months_are_listed_once_in_order():
    assert accepted()
    assert not accepted(hours_by_month=list(reversed(GOOD["hours_by_month"])))


def test_hours_never_exceed_capacity():
    assert accepted()
    assert not accepted(hours_by_month=[{"month": 3, "crew_hours": 170, "capacity": 160}])


def test_a_month_outside_the_year_is_refused():
    assert accepted(hours_by_month=[{"month": 12, "crew_hours": 0, "capacity": 0}])
    assert not accepted(hours_by_month=[{"month": 13, "crew_hours": 0, "capacity": 0}])


def test_an_empty_message_is_refused():
    assert accepted(message="ok")
    assert not accepted(message="")
