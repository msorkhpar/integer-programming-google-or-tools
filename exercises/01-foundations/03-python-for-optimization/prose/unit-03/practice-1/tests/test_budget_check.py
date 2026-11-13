from budget_check import years_over

# A crew-overtime plan unlike the lesson's portfolio, with spend as a solver would return it:
# floats, some a hair above a whole number. Budgets in $k.


def test_years_clearly_over_are_listed_in_order():
    spend = {2033: 912.0, 2031: 455.25, 2032: 300.0}
    budget = {2031: 450, 2032: 300, 2033: 900}
    assert years_over(spend, budget) == [2031, 2033]


def test_years_within_budget_are_not_listed():
    spend = {2031: 449.5, 2032: 0.0}
    budget = {2031: 450, 2032: 120}
    assert years_over(spend, budget) == []


def test_float_noise_above_the_budget_is_not_over():
    spend = {2031: 450.00000000001, 2032: 299.99999999998}
    budget = {2031: 450, 2032: 300}
    assert years_over(spend, budget) == []


def test_a_zero_budget_year_tolerates_noise_near_zero():
    spend = {2031: 3e-9, 2032: 450.0}
    budget = {2031: 0, 2032: 450}
    assert years_over(spend, budget) == []


def test_a_large_budget_gets_a_relative_tolerance():
    spend = {2031: 2_000_000_000.5}
    budget = {2031: 2_000_000_000}
    assert years_over(spend, budget) == []


def test_a_real_overrun_of_a_zero_budget_is_over():
    spend = {2031: 0.5, 2032: 450.0}
    budget = {2031: 0, 2032: 450}
    assert years_over(spend, budget) == [2031]
