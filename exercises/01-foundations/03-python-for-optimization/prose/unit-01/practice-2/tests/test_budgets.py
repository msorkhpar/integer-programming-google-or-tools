import io

import pandas as pd

from budgets import budget_problems

# A two-region, two-year plan unlike the lesson's portfolio. Budgets in $k. Line 1 is the header.
YEARS = [2031, 2032]
REGIONS = ["North", "South"]
HEADER = "year,region,budget\n"


def check(body: str) -> list[str]:
    return sorted(budget_problems(pd.read_csv(io.StringIO(HEADER + body)), YEARS, REGIONS))


CLEAN = """2031,North,500
2031,South,650
2032,North,520
2032,South,610
"""


def test_a_complete_clean_table_has_no_problems():
    assert check(CLEAN) == []


def test_a_negative_budget_is_reported():
    assert check(CLEAN.replace("2032,North,520", "2032,North,-20")) == ["line 4: negative budget"]


def test_an_unknown_region_is_reported():
    assert check(CLEAN + "2031,East,100\n") == ["line 6: unknown region"]


def test_a_zero_budget_is_allowed():
    assert check(CLEAN.replace("2032,South,610", "2032,South,0")) == []


def test_a_budget_written_with_a_comma_is_not_a_number():
    assert check(CLEAN.replace("2031,North,500", '2031,North,"1,200"')) == ["line 2: budget is not a number"]


def test_a_year_before_the_plan_is_outside_it():
    assert check(CLEAN + "2030,North,480\n") == ["line 6: year outside the plan"]


def test_every_copy_of_a_repeated_pair_is_reported():
    assert check(CLEAN + "2031,South,700\n") == ["line 3: duplicate", "line 6: duplicate"]


def test_a_missing_pair_is_reported_even_when_the_row_count_is_right():
    body = CLEAN.replace("2032,South,610", "2032,North,525")
    assert check(body) == ["line 4: duplicate", "line 5: duplicate", "missing 2032 South"]
