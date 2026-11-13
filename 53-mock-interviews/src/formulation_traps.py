"""Mock 1's traps, checked by a solver: a precedence row built from a time sum and big-M, and a
symmetry row that removes every copy of the best plan.

Each plan is fixed through the variables' bounds and HiGHS is asked whether the rows allow it
(lesson 12.3.1's test), so the verdicts depend on the rows and nothing else.
"""

from __future__ import annotations

from ortools.math_opt.python import mathopt

from mock_support import allowed, quiet_solve

YEARS = (2027, 2028, 2029, 2030, 2031)
DURATION_A = 2     # the parent takes two years
GAP = 1            # the child may start one year after the parent finishes
LAG = DURATION_A + GAP                          # the same rule, start to start: 3 years


def precedence_model(form: str) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name=f"precedence-{form}")
    x = {(p, t): model.add_binary_variable(name=f"x_{p}_{t}") for p in "AB" for t in YEARS}
    for p in "AB":
        model.add_linear_constraint(sum(x[p, t] for t in YEARS) <= 1, name=f"once_{p}")
    if form == "time sum and big-M":
        big_m = max(YEARS) + LAG                # the most the right side can reach when B is unfunded
        start_b = sum(t * x["B", t] for t in YEARS)
        earliest_b = sum((t + LAG) * x["A", t] for t in YEARS)
        funded_b = sum(x["B", t] for t in YEARS)
        model.add_linear_constraint(start_b >= earliest_b - big_m * (1 - funded_b), name="after_B")
    else:
        for t in YEARS:                         # B started by t only if A had started by t - LAG
            b_by_t = sum(x["B", u] for u in YEARS if u <= t)
            a_by_lag = sum(x["A", s] for s in YEARS if s <= t - LAG)
            model.add_linear_constraint(b_by_t - a_by_lag <= 0, name=f"after_B_{t}")
    return model, x


def symmetry_model(rows: str) -> tuple[mathopt.Model, dict]:
    """Two identical projects S1 and S2, each $100k and worth 50, and $100k to spend each year."""
    model = mathopt.Model(name=f"symmetry-{rows}")
    starts = (2027, 2028)
    x = {(p, t): model.add_binary_variable(name=f"x_{p}_{t}") for p in ("S1", "S2") for t in starts}
    for p in ("S1", "S2"):
        model.add_linear_constraint(sum(x[p, t] for t in starts) <= 1, name=f"once_{p}")
    for t in starts:
        model.add_linear_constraint(100 * x["S1", t] + 100 * x["S2", t] <= 100, name=f"budget_{t}")
    for t in starts:
        if rows == "same-year order":           # x[S1,t] >= x[S2,t]
            model.add_linear_constraint(x["S1", t] - x["S2", t] >= 0, name=f"order_{t}")
        elif rows == "started-by order":        # S1 has started by t whenever S2 has
            s1_by = sum(x["S1", u] for u in starts if u <= t)
            s2_by = sum(x["S2", u] for u in starts if u <= t)
            model.add_linear_constraint(s1_by - s2_by >= 0, name=f"order_{t}")
    model.maximize(sum(50 * v for v in x.values()))
    return model, x


def main() -> None:
    plans = {
        "A unfunded, B in 2028": {("B", 2028): 1},
        "A in 2027, B in 2030": {("A", 2027): 1, ("B", 2030): 1},
        "A in 2027, B in 2029": {("A", 2027): 1, ("B", 2029): 1},
    }
    print(f"child B may start {LAG} years after parent A starts (A lasts {DURATION_A} years, then a {GAP}-year gap)")
    print(f"  {'plan':<22} {'time sum and big-M':<20} cumulative rows")
    for name, plan in plans.items():
        verdicts = []
        for form in ("time sum and big-M", "cumulative rows"):
            model, x = precedence_model(form)
            verdicts.append("allowed" if allowed(model, x, plan) else "refused")
        print(f"  {name:<22} {verdicts[0]:<20} {verdicts[1]}")
    print()
    print("two identical projects, one start a year fits the budget")
    for rows in ("no order rows", "same-year order", "started-by order"):
        model, x = symmetry_model(rows)
        result = quiet_solve(model)
        plan = sorted(f"{p} {t}" for (p, t), v in x.items() if result.variable_values(v) > 0.5)
        print(f"  {rows:<17} best value {result.objective_value():>4.0f}  plan: {', '.join(plan)}")


if __name__ == "__main__":
    main()
