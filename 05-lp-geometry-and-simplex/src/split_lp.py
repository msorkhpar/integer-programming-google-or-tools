"""GridCap's two-program budget split, the LP that module 05 draws, walks and breaks.

GridCap is fictional. A planner splits next year's maintenance money between distribution work
(d) and transmission work (t), both in units of $100k. Every row reads  a_d * d + a_t * t <= b.
"""

from ortools.math_opt.python import mathopt

NAMES = ("d", "t")
ROWS = {
    "budget": ((1, 1), 30),     # $3.0M in all
    "crews": ((3, 2), 72),      # 72 crew-weeks; $100k of distribution takes 3, of transmission 2
    "ready_t": ((0, 1), 20),    # only $2.0M of transmission work is designed and ready
}
BOUNDS = {
    "d_nonneg": ((-1, 0), 0),   # d >= 0, written as -d <= 0
    "t_nonneg": ((0, -1), 0),   # t >= 0
}
VALUE = (5, 4)                  # risk points removed per $100k of d and of t


def build(rows=ROWS, value=VALUE) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="budget-split")
    x = {name: model.add_variable(lb=0, name=name) for name in NAMES}
    for label, ((a_d, a_t), b) in rows.items():
        model.add_linear_constraint(a_d * x["d"] + a_t * x["t"] <= b, name=label)
    model.maximize(value[0] * x["d"] + value[1] * x["t"])
    return model, x


if __name__ == "__main__":
    model, x = build()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    print("GLOP:", result.termination.reason.name,
          f"d = {result.variable_values(x['d']):g}, t = {result.variable_values(x['t']):g},",
          f"value = {result.objective_value():g}")
