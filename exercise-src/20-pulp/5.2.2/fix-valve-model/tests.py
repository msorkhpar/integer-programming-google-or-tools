import warnings

from valves import Valve, plan

warnings.simplefilter("ignore")      # PuLP 3.3's deprecation and objective warnings; the tests judge results

# A gas utility's valve replacements, not the lesson's portfolio.
MAINS = [
    Valve("H1", "harbor", 30, 40, 3),
    Valve("H2", "harbor", 22, 30, 2),
    Valve("U1", "uptown", 25, 20, 4),
    Valve("U2", "uptown", 18, 25, 1),
    Valve("U3", "uptown", 10, 15, 1),
]


def test_best_plan_when_crews_are_the_limit():
    assert plan(MAINS, budget=90, crew_weeks=7, harbor_band=(0, 100), last_year={}) == (65, ["H2", "U1", "U2"])


def test_best_plan_when_money_is_the_limit():
    assert plan(MAINS, budget=90, crew_weeks=100, harbor_band=(0, 100), last_year={}) == (77, ["H1", "H2", "U1"])


def test_last_years_valves_stay_in_the_plan():
    kept = {"U3": 1.0, "U1": 0.0}
    assert plan(MAINS, budget=90, crew_weeks=7, harbor_band=(0, 100), last_year=kept) == (62, ["H1", "H2", "U3"])


def test_harbor_gets_at_least_its_floor():
    assert plan(MAINS, budget=90, crew_weeks=7, harbor_band=(60, 100), last_year={}) == (62, ["H1", "H2", "U3"])


def test_rules_that_cannot_all_hold_give_no_plan():
    too_many = {"H1": 1.0, "H2": 1.0, "U1": 1.0}       # 9 crew-weeks against 7
    assert plan(MAINS, budget=90, crew_weeks=7, harbor_band=(0, 100), last_year=too_many) is None
