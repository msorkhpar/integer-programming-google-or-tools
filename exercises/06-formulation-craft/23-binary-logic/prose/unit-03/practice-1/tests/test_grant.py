from ortools.math_opt.python import mathopt

from grant import Tower, build

# A carrier's towers in three counties, not the lesson's portfolio.
TOWERS = ([Tower(f"A{k}", "Alder") for k in range(1, 5)] + [Tower(f"B{k}", "Birch") for k in range(1, 4)]
          + [Tower(f"C{k}", "Cedar") for k in range(1, 4)])
NEED = {"Alder": 2, "Birch": 3, "Cedar": 1}
ALREADY = {"Birch": 2}
CREW_LIMIT = {"Alder": 3, "Cedar": 2}
BACKHAUL = {"A1": ["A1-fiber", "A1-radio"], "C1": ["C1-fiber", "C1-radio", "C1-sat"]}

GOOD = {"A1", "A1-fiber", "A2", "B1", "B2", "B3", "C2"}


def allowed(plan: set[str]) -> bool:
    """Fix every tower and backhaul option to the plan and ask whether the model accepts it."""
    model, x, y = build(TOWERS, NEED, ALREADY, CREW_LIMIT, BACKHAUL)
    for key, var in {**x, **y}.items():
        var.lower_bound = var.upper_bound = 1.0 if key in plan else 0.0
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_each_county_reaches_its_coverage_target():
    assert allowed(GOOD) is True
    assert allowed(GOOD - {"A2"}) is False


def test_a_county_gets_no_more_upgrades_than_its_crews_can_do():
    assert allowed(GOOD | {"A3"}) is True
    assert allowed(GOOD | {"A3", "A4"}) is False


def test_an_upgraded_hub_gets_a_backhaul_link():
    assert allowed(GOOD) is True
    assert allowed(GOOD - {"A1-fiber"}) is False


def test_towers_upgraded_earlier_count_toward_the_target():
    assert allowed({"A1", "A1-fiber", "A2", "B1", "C2"}) is True
    assert allowed({"A1", "A1-fiber", "A2", "C2"}) is False


def test_a_hub_gets_one_backhaul_link_not_two():
    assert allowed(GOOD) is True
    assert allowed(GOOD | {"A1-radio"}) is False


def test_a_hub_that_is_not_upgraded_gets_no_backhaul():
    assert allowed(GOOD) is True
    assert allowed(GOOD | {"C1-sat"}) is False
