from ortools.math_opt.python import mathopt

from relining import Pipe, build

# A water utility's cast-iron mains, not the lesson's portfolio.
PIPES = [Pipe("P1", 10.0, 4.0), Pipe("P2", 8.0, 6.0), Pipe("P3", 12.0, 3.0), Pipe("P4", 6.0, 3.0)]
T_LOW, T_HIGH, SUPPLY = 3.0, 8.0, 100.0


def allowed(plan: set[str], thickness: float) -> bool:
    """Fix which pipes are relined and the thickness, and ask whether the model accepts the plan."""
    model, x, t = build(PIPES, T_LOW, T_HIGH, SUPPLY)
    for pid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if pid in plan else 0.0
    t.lower_bound = t.upper_bound = thickness
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_the_resin_used_fits_the_supply():
    assert allowed({"P2"}, 6.0) is True                        # 8 x 6 = 48 kg
    assert allowed({"P1", "P2", "P3", "P4"}, 6.0) is False     # 36 x 6 = 216 kg


def test_a_relined_pipe_gets_at_least_its_minimum_thickness():
    assert allowed({"P2"}, 6.0) is True
    assert allowed({"P2"}, 5.0) is False                       # P2 needs 6 mm


def test_resin_is_counted_at_the_chosen_thickness():
    assert allowed({"P1"}, 6.0) is True                        # 60 kg
    assert allowed({"P1", "P3"}, 6.0) is False                 # 22 x 6 = 132 kg; at 3 mm it would be 66


def test_a_pipe_that_is_not_relined_sets_no_minimum():
    assert allowed({"P1", "P4"}, 4.0) is True                  # P2's 6 mm does not apply
    assert allowed({"P2", "P4"}, 4.0) is False
