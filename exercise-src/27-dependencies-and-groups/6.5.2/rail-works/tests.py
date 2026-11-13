from ortools.math_opt.python import mathopt

from rail import Project, build

# A rail line's works, not the lesson's portfolio.
PROJECTS = [
    Project("SIG-A1", (2027, 2028, 2029)),
    Project("SIG-A2", (2028, 2029, 2030)),
    Project("SIG-A3", (2027, 2028, 2029)),
    Project("SIG-B1", (2029, 2030)),
    Project("SIG-B2", (2029, 2030)),
    Project("PLAT-N", (2029, 2030)),
    Project("TRK-1", (2027, 2028, 2029)),
    Project("TRK-2", (2028, 2029, 2030)),
]
BLOCKS = [["SIG-A1", "SIG-A2", "SIG-A3"], ["SIG-B1", "SIG-B2"]]
PLATFORMS = {"PLAT-N": ["TRK-1", "TRK-2"]}


def allowed(plan: set[tuple[str, int]]) -> bool:
    """Fix every start variable to the plan and ask whether the model accepts it."""
    model, x = build(PROJECTS, BLOCKS, PLATFORMS)
    for key, var in x.items():
        value = 1.0 if key in plan else 0.0
        if value > var.upper_bound:
            return False
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


BLOCK_A = {("SIG-A1", 2029), ("SIG-A2", 2029), ("SIG-A3", 2029)}


def test_a_signal_block_is_upgraded_whole():
    assert allowed(BLOCK_A) is True
    assert allowed({("SIG-A1", 2029), ("SIG-A3", 2029)}) is False
    assert allowed({("SIG-B1", 2030)}) is False


def test_a_platform_needs_a_track_upgrade_first():
    assert allowed({("TRK-1", 2027), ("TRK-2", 2028), ("PLAT-N", 2029)}) is True
    assert allowed({("PLAT-N", 2029)}) is False


def test_a_signal_block_starts_in_one_year():
    assert allowed({("SIG-B1", 2030), ("SIG-B2", 2030)}) is True
    assert allowed({("SIG-B1", 2029), ("SIG-B2", 2030)}) is False
    assert allowed({("SIG-A1", 2028), ("SIG-A2", 2028), ("SIG-A3", 2029)}) is False


def test_one_track_upgrade_is_enough():
    assert allowed({("TRK-2", 2028), ("PLAT-N", 2030)}) is True
    assert allowed({("TRK-2", 2028)}) is True
    assert allowed({("PLAT-N", 2030)}) is False


def test_the_track_upgrade_must_be_a_year_ahead():
    assert allowed({("TRK-2", 2029), ("PLAT-N", 2030)}) is True
    assert allowed({("TRK-2", 2029), ("PLAT-N", 2029)}) is False
