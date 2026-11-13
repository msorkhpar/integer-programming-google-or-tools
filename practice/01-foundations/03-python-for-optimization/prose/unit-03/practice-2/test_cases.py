import pytest

from cases import BASE, CASES, RULES, check_request

# The team's suite runs one test per row of CASES:
#     @pytest.mark.parametrize(("row", "rule"), CASES)
# These tests check that the table is fit for that.


def test_the_table_has_six_requests_each_naming_a_rule():
    assert len(CASES) == 6
    for row, rule in CASES:
        assert isinstance(row, dict) and set(row) == set(BASE), f"{row} is not a request like BASE"
        assert rule in RULES, f"{rule!r} is not a rule name"


def test_each_case_is_rejected_for_the_rule_it_names():
    assert len(CASES) == 6
    for row, rule in CASES:
        assert rule in check_request(row), f"{row} is not rejected for {rule}"


def test_each_case_breaks_only_its_rule():
    assert len(CASES) == 6
    for row, rule in CASES:
        assert check_request(row) == [rule], f"{row} breaks {check_request(row)}, not only {rule}"


def test_the_cases_cover_all_six_rules():
    assert len(CASES) == 6
    assert sorted(rule for _, rule in CASES) == sorted(RULES)


def test_the_base_request_is_untouched():
    assert len(CASES) == 6
    assert BASE == {"feeder": "F-12", "crew": "line-1", "start_week": "10", "end_week": "12", "hours": "36",
                    "priority": "2"}
    assert all(row is not BASE for row, _ in CASES)
