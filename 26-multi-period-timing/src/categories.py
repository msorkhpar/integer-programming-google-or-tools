"""Budget categories: each project draws from separate pots, and each pot has its own row per year."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from timing_model import build, schedule, solve_highs

small = generate("small")
exact = mathopt.SolveParameters(relative_gap_tolerance=0.0)

# GridCap has no budget categories, so this split is invented for the lesson (GridCap is fictional).
POTS = ("capex", "opex", "fund")
OPEX_SHARE = {"trim": 1.0, "clear": 1.0, "widen": 1.0, "repair": 0.4}   # maintenance work runs on OpEx
FUND_SHARE = {"underground": 0.5}                                       # a resilience fund pays half
POT_BUDGET_SHARE = {"opex": 0.25, "fund": 0.10}                         # of B_y; CapEx gets the rest


def profile(p) -> dict[str, tuple[int, ...]]:
    """c[i,k,tau]: what project p draws from pot k in its tau-th year of work, in $k."""
    opex = tuple(10 * round(c * OPEX_SHARE.get(p.intervention, 0) / 10) for c in p.cost_profile)
    fund = tuple(10 * round(c * FUND_SHARE.get(p.intervention, 0) / 10) for c in p.cost_profile)
    capex = tuple(c - o - f for c, o, f in zip(p.cost_profile, opex, fund))
    return {"capex": capex, "opex": opex, "fund": fund}


def pot_budget() -> dict[tuple[str, int], int]:
    """B[k,y]: each year's budget split into pots that add up to it."""
    budget = {}
    for y, total in small.budget.items():
        for k, share in POT_BUDGET_SHARE.items():
            budget[k, y] = 10 * round(total * share / 10)
        budget["capex", y] = total - sum(budget[k, y] for k in POT_BUDGET_SHARE)
    return budget


B = pot_budget()


def draw_by_year(tm, pot: str) -> dict[int, mathopt.LinearExpression]:
    """What the plan draws from one pot in each calendar year."""
    draw = {y: mathopt.LinearExpression() for y in small.years}
    for p in small.projects:
        c = profile(p)[pot]
        for t in p.starts():
            for tau, amount in enumerate(c):
                if amount:
                    draw[t + tau] += amount * tm.x[p.project_id, t]
    return draw


def with_categories(drop: str | None = None):
    """The timing model with one row per pot and year; `drop` names one row to leave out."""
    tm = build(small)                                  # keeps the pooled budget_y rows
    for k in POTS:
        draw = draw_by_year(tm, k)
        for y in small.years:
            if f"{k}_{y}" != drop:
                tm.model.add_linear_constraint(draw[y] <= B[k, y], name=f"{k}_{y}")
    return tm, solve_highs(tm.model, exact)


def pot_spend(plan: dict[str, int]) -> dict[tuple[str, int], int]:
    """What a fixed plan draws from each pot in each year."""
    spend = {(k, y): 0 for k in POTS for y in small.years}
    for pid, t in plan.items():
        for k, c in profile(small.project(pid)).items():
            for tau, amount in enumerate(c):
                spend[k, t + tau] += amount
    return spend


if __name__ == "__main__":
    for pid in ("P017", "P034", "P039", "P035"):
        p = small.project(pid)
        print(f"{pid} {p.intervention:11} c[k,tau]:", ", ".join(f"{k} {c}" for k, c in profile(p).items()))
    print("pot budgets 2027:", "  ".join(f"{k} {B[k, 2027]:,}" for k in POTS), f"(sum {small.budget[2027]:,} = B_2027)")

    pooled = build(small)
    result = solve_highs(pooled.model, exact)
    pooled_npv = result.objective_value()
    spend = pot_spend(schedule(pooled, result))
    print(f"one pooled budget  NPV ${pooled_npv:,.0f}k, fits every budget_y row, but breaks:")
    for k in POTS:
        broken = [f"{k}_{y} {spend[k, y]:,} > {B[k, y]:,}" for y in small.years if spend[k, y] > B[k, y]]
        print("  " + ", ".join(broken))

    tm, result = with_categories()
    npv, plan = result.objective_value(), schedule(tm, result)
    spend = pot_spend(plan)
    print(f"with pots          NPV ${npv:,.0f}k ({npv - pooled_npv:+,.0f}k)")
    gain = {}
    for k in POTS:
        for y in small.years:
            gain[f"{k}_{y}"] = with_categories(drop=f"{k}_{y}")[1].objective_value() - npv
    top = sorted((g, row) for row, g in gain.items() if g > 0.5)[::-1][:4]
    print("drop one row alone, NPV gain:", ", ".join(f"{row} {g:+,.0f}k" for g, row in top))
    print("fund_2027 slack with pots:", B["fund", 2027] - spend["fund", 2027])
    p034 = small.project("P034")
    tm_relaxed, relaxed = with_categories(drop="fund_2027")
    print(f"P034 starts in {schedule(tm_relaxed, relaxed).get('P034')} without fund_2027,"
          f" {'in ' + str(plan['P034']) if 'P034' in plan else 'never'} with it; window {p034.earliest_start}-{p034.latest_start},"
          f" NPV by start {dict(p034.npv)}")
