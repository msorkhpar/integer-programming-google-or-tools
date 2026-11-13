"""Which model features each MathOpt solver in the runner accepts, asked with three tiny models (lesson 5.4.1).

A feature a solver lacks shows up in one of two ways: a refusal (an exception whose reason, in
OR-Tools 9.15.6755, is on `__context__`; lesson 4.2.4), or a quiet change to the model.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

S = mathopt.SolverType
SOLVERS = (("HiGHS", S.HIGHS), ("SCIP", S.GSCIP), ("CP-SAT", S.CP_SAT))


def continuous() -> mathopt.Model:
    """max 1.01a + 2.9b, 0.37a + 1.13b <= 7.71, a in [0, 10] continuous, b in {0..10}: optimum 20.3078."""
    m = mathopt.Model(name="continuous")
    a = m.add_variable(lb=0, ub=10, name="a")
    b = m.add_integer_variable(lb=0, ub=10, name="b")
    m.add_linear_constraint(0.37 * a + 1.13 * b <= 7.71, name="cap")
    m.maximize(1.01 * a + 2.9 * b)
    return m


def quadratic() -> mathopt.Model:
    """min (a - 3)^2 + (b - 6)^2, a + b <= 7, a, b in {0..10}: optimum 2 (a = 2, b = 5)."""
    m = mathopt.Model(name="quadratic")
    a = m.add_integer_variable(lb=0, ub=10, name="a")
    b = m.add_integer_variable(lb=0, ub=10, name="b")
    m.add_linear_constraint(a + b <= 7, name="cap")
    m.minimize((a - 3) * (a - 3) + (b - 6) * (b - 6))
    return m


def indicator() -> mathopt.Model:
    """max a + 2z, z = 1 implies a <= 3, a in {0..10}, z binary: optimum 10 (z = 0, a = 10)."""
    m = mathopt.Model(name="indicator")
    z = m.add_binary_variable(name="z")
    a = m.add_integer_variable(lb=0, ub=10, name="a")
    m.add_indicator_constraint(indicator=z, implied_constraint=a <= 3, name="small_if_z")
    m.maximize(a + 2 * z)
    return m


for make in (continuous, quadratic, indicator):
    print(f"{make.__name__}: {make.__doc__.split(':')[0]}")
    for name, kind in SOLVERS:
        model = make()
        try:
            result = mathopt.solve(model, kind)
            values = ", ".join(f"{v.name} = {result.variable_values(v):g}" for v in model.variables())
            print(f"  {name:<7} {result.termination.reason.name}, objective {result.objective_value():.4f} ({values})")
        except Exception as error:
            reason = getattr(error.__context__, "message", str(error))
            print(f"  {name:<7} refused: {reason}")
