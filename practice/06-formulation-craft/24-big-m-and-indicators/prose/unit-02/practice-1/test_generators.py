from ortools.math_opt.python import mathopt

from generators import bounds, build, tight_m

SITES = {"A": (40, 30, 500), "B": (25, 80, 300), "C": (30, 50, 900)}
FLEET = 100


def allowed(hours: dict[str, float], hooked: set[str]) -> bool:
    model, h, hook = build(SITES, FLEET, tight_m(SITES, FLEET))
    for s in SITES:
        h[s].lower_bound = h[s].upper_bound = hours.get(s, 0.0)
        hook[s].lower_bound = hook[s].upper_bound = 1.0 if s in hooked else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_generator_hours_need_a_hookup():
    assert allowed({"A": 10}, {"A"}) is True
    assert allowed({"A": 10}, set()) is False


def test_a_hooked_site_may_use_all_its_demand():
    assert allowed({"A": 30, "B": 70}, {"A", "B"}) is True
    assert allowed({"A": 30, "B": 70}, {"A"}) is False


def test_m_is_the_smaller_of_demand_and_fleet():
    assert tight_m(SITES, FLEET) == {"A": 30, "B": 80, "C": 50}
    assert tight_m({"B": (25, 180, 300)}, FLEET) == {"B": 100}


def test_the_tight_m_lowers_the_lp_bound_and_keeps_the_best_plan():
    b = bounds(SITES, FLEET)
    assert b["loose"] > 3199                       # with M = 1e6 the fees all but vanish from the LP
    assert abs(b["tight"] - 2187.5) < 1e-6
    assert abs(b["milp"] - 2150) < 1e-6
