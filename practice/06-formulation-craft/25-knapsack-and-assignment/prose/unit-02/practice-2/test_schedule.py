from ortools.math_opt.python import mathopt

from schedule import Crew, Job, build

# A water utility's main replacements and its contractor crews, not the lesson's portfolio.
YEARS = [2027, 2028, 2029]
CREWS = [Crew("Kim", {2027: 20, 2028: 20, 2029: 10}, 9, certified=True),
         Crew("Lee", {2027: 15, 2028: 15, 2029: 15}, 7)]
JOBS = [Job("M1", 2027, 2028, {"Kim": 10, "Lee": 12}),
        Job("M2", 2027, 2029, {"Kim": 8, "Lee": 8}),
        Job("M3", 2028, 2029, {"Kim": 12, "Lee": 14}, large=True),
        Job("M4", 2027, 2027, {"Kim": 6, "Lee": 9})]


def allowed(plan: dict[str, tuple[str, int]]) -> bool:
    """plan: job -> (crew, year). A pair the model has no variable for is refused outright."""
    model, x = build(JOBS, CREWS, YEARS)
    wanted = {(jid, cid, t) for jid, (cid, t) in plan.items()}
    if not wanted <= set(x):
        return False
    for key, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if key in wanted else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


GOOD = {"M1": ("Kim", 2027), "M2": ("Lee", 2028), "M3": ("Kim", 2028), "M4": ("Lee", 2027)}


def test_every_job_is_done_exactly_once():
    assert allowed(GOOD) is True
    assert allowed({k: v for k, v in GOOD.items() if k != "M2"}) is False


def test_a_crew_works_within_its_weeks_each_year_at_its_own_pace():
    # Lee in 2027: M1 (12) + M4 (9) = 21 weeks of 15. Kim would need only 16 of 20 for the two.
    assert allowed({"M1": ("Kim", 2027), "M2": ("Lee", 2028), "M3": ("Kim", 2028), "M4": ("Kim", 2027)}) is True
    assert allowed({"M1": ("Lee", 2027), "M2": ("Kim", 2028), "M3": ("Kim", 2028), "M4": ("Lee", 2027)}) is False


def test_a_job_is_done_inside_its_window():
    # M1 may be done in 2027 or 2028 only.
    assert allowed({"M1": ("Lee", 2028), "M2": ("Lee", 2029), "M3": ("Kim", 2028), "M4": ("Lee", 2027)}) is True
    assert allowed({"M1": ("Kim", 2029), "M2": ("Lee", 2028), "M3": ("Kim", 2028), "M4": ("Lee", 2027)}) is False


def test_a_large_main_needs_a_certified_crew():
    assert allowed(GOOD) is True
    assert allowed({"M1": ("Kim", 2027), "M2": ("Kim", 2028), "M3": ("Lee", 2028), "M4": ("Lee", 2027)}) is False
