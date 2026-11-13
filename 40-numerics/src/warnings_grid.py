"""Which magnitudes make HiGHS print a warning? One small model per magnitude, each with one large or small number."""

from ortools.math_opt.python import mathopt

from loan_model import solve


def one_number(kind: str, value: float) -> mathopt.Model:
    """max x + y  s.t.  a x + y <= b,  0 <= x <= u,  y in {0, 1}; one of a, cost, b, u set to `value`."""
    a, cost, b, u = 1.0, 1.0, 1.0, 1.0
    if kind == "Matrix":
        a = value
    elif kind == "Cost":
        cost = value
    elif kind == "RHS":
        b = value
    else:
        u = value
    model = mathopt.Model(name="one")
    x = model.add_variable(lb=0, ub=u, name="x")
    y = model.add_binary_variable(name="y")
    model.add_linear_constraint(a * x + y <= b, name="row")
    model.maximize(cost * x + y)
    return model


for kind in ("Matrix", "Cost", "RHS", "Bound"):
    for value in (1e-7, 1e5, 1e6, 1e7, 1e11):
        _, log = solve(one_number(kind, value))
        warnings = [line.replace("WARNING: ", "").strip() for line in log if line.startswith("WARNING")]
        print(f"{kind:6} {value:.0e}: {' / '.join(warnings) if warnings else 'no warning'}")
