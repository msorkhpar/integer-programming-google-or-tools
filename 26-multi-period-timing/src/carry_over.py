"""Let unspent budget roll into the next year, and cap a multi-year window."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build, solve_highs

small = generate("small")
exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def with_carry_over(max_share: float | None = None, window_cap: tuple[tuple[int, ...], int] | None = None,
                    lapse: bool = True):
    tm = build(small)
    carry = {}
    for y in small.years:
        tm.model.delete_linear_constraint(tm.budget[y])
        carry[y] = tm.model.add_variable(lb=0, name=f"carry_{y}")      # unspent at the end of y
    for i, y in enumerate(small.years):
        incoming = carry[small.years[i - 1]] if i else 0
        # <=, not ==: money neither spent nor carried lapses at the end of the year.
        flow = tm.spend[y] + carry[y] - small.budget[y] - incoming
        tm.model.add_linear_constraint((flow <= 0) if lapse else (flow == 0), name=f"cash_{y}")
        if max_share is not None:
            tm.model.add_linear_constraint(carry[y] <= max_share * small.budget[y], name=f"carry_cap_{y}")
    if window_cap is not None:
        years, cap = window_cap
        tm.model.add_linear_constraint(sum(tm.spend[y] for y in years) <= cap, name="window_cap")
    result = solve_highs(tm.model, exact)
    if not result.has_primal_feasible_solution():
        return result, {}
    return result, {y: round(result.variable_values(carry[y])) for y in small.years}


if __name__ == "__main__":
    base = solve_highs(build(small).model, exact)
    print(f"no carry-over          NPV ${base.objective_value():,.0f}k")
    cap = 10 * (9 * (small.budget[2030] + small.budget[2031]) // 100)     # 90% of the two years' budgets
    for label, kwargs in (("unlimited carry-over", {}), ("carry-over <= 10%", {"max_share": 0.1}),
                          ("plus 2030-31 cap", {"max_share": 0.1, "window_cap": ((2030, 2031), cap)})):
        result, carry = with_carry_over(**kwargs)
        print(f"{label:22} NPV ${result.objective_value():,.0f}k  carried {carry}")
    print("budgets:", dict(small.budget), f"2030-31 cap: {cap:,}")
    result, _ = with_carry_over(max_share=0.1, window_cap=((2030, 2031), cap), lapse=False)
    print(f"{'== instead of <=':22} {result.termination.reason.name}")
