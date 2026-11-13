"""A disjunction over one variable's intervals: with tight Ms, big-M and the hull give the same LP."""

from ortools.math_opt.python import mathopt

# A vegetation contract is either small, 100 to 300 $k, or large, 600 to 900 $k (large = 1).
SMALL, LARGE = (100, 300), (600, 900)


def build(form: str, big_m: float | None = None):
    model = mathopt.Model(name=form)
    s = model.add_variable(lb=SMALL[0], ub=LARGE[1], name="s")
    large = model.add_variable(lb=0, ub=1, name="large")          # relaxed: the LP view
    if form == "big_m":
        up = LARGE[1] - SMALL[1] if big_m is None else big_m           # tight: the most s can exceed 300
        down = LARGE[0] - SMALL[0] if big_m is None else big_m         # tight: the most s can fall below 600
        model.add_linear_constraint(s <= SMALL[1] + up * large, name="small_cap")
        model.add_linear_constraint(s >= LARGE[0] - down * (1 - large), name="large_floor")
    else:
        s_small = model.add_variable(lb=0, name="s_small")
        s_large = model.add_variable(lb=0, name="s_large")
        model.add_linear_constraint(s == s_small + s_large, name="split")
        model.add_linear_constraint(SMALL[0] * (1 - large) <= s_small, name="small_lo")
        model.add_linear_constraint(s_small <= SMALL[1] * (1 - large), name="small_hi")
        model.add_linear_constraint(LARGE[0] * large <= s_large, name="large_lo")
        model.add_linear_constraint(s_large <= LARGE[1] * large, name="large_hi")
    return model, s, large


objectives = {"max s - 450 large": (1, -450, True), "min s + 200 large": (1, 200, False),
              "max 2 s - 1300 large": (2, -1300, True), "min 3 s - 900 large": (3, -900, False)}
print("objective              tight big-M     hull   big-M with M = 10,000")
for name, (a, b, maximize) in objectives.items():
    values = []
    for form, big_m in (("big_m", None), ("hull", None), ("big_m", 10_000)):
        model, s, large = build(form, big_m)
        (model.maximize if maximize else model.minimize)(a * s + b * large)
        values.append(mathopt.solve(model, mathopt.SolverType.GLOP).objective_value())
    print(f"{name:22} {values[0]:10.1f}  {values[1]:7.1f}  {values[2]:10.1f}")
