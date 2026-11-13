from ortools.math_opt.python import mathopt

from bonus import build

# Two substations of a transmission operator's programme; not the lesson's portfolio.
COST = {"T1": 4, "T2": 3, "B1": 2, "B2": 5, "F1": 3}
VALUE = {"T1": 1, "T2": 1, "B1": 1, "B2": 2, "F1": 3}
JOBS = {"North": ["T1", "T2", "B1"], "East": ["B2"]}
BONUS = {"North": 9, "East": 4}


def allowed(funded: set, commissioned: set, jobs_of=JOBS) -> bool:
    model, x, z = build(COST, VALUE, 100, {s: 1 for s in jobs_of}, jobs_of)
    for j, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if j in funded else 0.0
    for s, var in z.items():
        var.lower_bound = var.upper_bound = 1.0 if s in commissioned else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def bounds(budget: int) -> tuple[float, float]:
    """The LP bound with your rows, and the best plan's value."""
    lp, _, _ = build(COST, VALUE, budget, BONUS, JOBS, integer=False)
    milp, _, _ = build(COST, VALUE, budget, BONUS, JOBS)
    return (mathopt.solve(lp, mathopt.SolverType.GLOP).objective_value(),
            mathopt.solve(milp, mathopt.SolverType.HIGHS).objective_value())


def test_a_substation_counts_only_with_every_job_funded():
    assert allowed({"T1", "T2", "B1"}, {"North"}) is True
    assert allowed({"T1", "T2"}, {"North"}) is False
    assert allowed({"T1", "T2"}, set()) is True


def test_a_substation_with_one_job_needs_that_job():
    assert allowed({"B2"}, {"East"}) is True
    assert allowed(set(), {"East"}) is False


def test_the_lp_bound_is_the_tight_one():
    # Budget 9: the best plans are worth 12 (North's three jobs and its bonus, for one). Rows that tie
    # z to each job give an LP bound of exactly 12; one row per substation lets the LP promise 12.8.
    lp, best = bounds(9)
    assert best == 12
    assert lp <= 12 + 1e-6
