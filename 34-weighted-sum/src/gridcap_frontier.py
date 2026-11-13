"""Every Pareto-optimal plan of GridCap small, which of them a weighted sum can reach, and one it cannot."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from two_objectives import build, plan_of, score, solve_highs

small = generate("small")
sm = build(small)


def frontier(sm) -> list[tuple[int, float]]:
    """Every Pareto point (NPV, risk), by an epsilon sweep on NPV in $1k steps (lesson 8.3.1)."""
    points, floor = [], None
    while True:
        rows = [] if floor is None else [sm.model.add_linear_constraint(sm.npv_of() >= floor, name="npv_floor")]
        sm.model.maximize(sm.risk_of())                       # pass 1: the most risk at this NPV floor
        result = solve_highs(sm.model)
        if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
            for row in rows:                                  # no plan reaches this floor: done
                sm.model.delete_linear_constraint(row)
            return points
        rows.append(sm.model.add_linear_constraint(sm.risk_of() >= result.objective_value() - 1e-6))
        sm.model.maximize(sm.npv_of())                        # pass 2: the most NPV at that risk
        npv, risk = score(sm, plan_of(sm, solve_highs(sm.model)))
        points.append((npv, risk))
        floor = npv + 1                                       # NPV is whole $k: the next point has more
        for row in rows:
            sm.model.delete_linear_constraint(row)


def supported(points: list[tuple[int, float]]) -> list[tuple[int, float]]:
    """The points on the upper-right convex hull of a Pareto front: the ones a weighted sum can reach."""
    hull = []
    for p in sorted(points):                                  # NPV up, so risk down along the front
        while len(hull) >= 2:
            (n1, r1), (n2, r2) = hull[-2], hull[-1]
            if (n2 - n1) * (p[1] - r1) - (r2 - r1) * (p[0] - n1) > 1e-9:
                hull.pop()                                    # hull[-1] lies below the line to p
            else:
                break
        hull.append(p)
    return hull


front = frontier(sm)
hull = supported(front)
print(f"{len(front)} Pareto-optimal plans, {len(hull)} supported, {len(front) - len(hull)} unsupported")
print("supported:", ", ".join(f"({n:,}, {r:,.0f})" for n, r in hull))


def below_hull(point) -> float:
    """How far (risk, $k) a point lies below the hull segment over its NPV."""
    a = max(h for h in hull if h[0] <= point[0])
    b = min(h for h in hull if h[0] >= point[0])
    if a == b:
        return 0.0
    return a[1] + (b[1] - a[1]) * (point[0] - a[0]) / (b[0] - a[0]) - point[1]


gaps = sorted(((below_hull(p), p) for p in front if p not in hull), reverse=True)
print("deepest unsupported plans, $k of risk below the hull:",
      ", ".join(f"({n:,}, {r:,.0f}) {g:,.0f}" for g, (n, r) in gaps[:3]))

# The planners' question: the most risk removed while keeping 95% of the best NPV.
floor = 0.95 * max(n for n, _ in front)
row = sm.model.add_linear_constraint(sm.npv_of() >= floor, name="npv_floor")
sm.model.maximize(sm.risk_of())
q = score(sm, plan_of(sm, solve_highs(sm.model)))
print(f"most risk with NPV >= ${floor:,.0f}k: NPV ${q[0]:,}k, risk ${q[1]:,.0f}k; "
      f"Pareto point: {q in front}, supported: {q in hull}")

a = max(h for h in hull if h[0] < q[0])                      # the supported neighbours around q
b = min(h for h in hull if h[0] > q[0])
low = (a[1] - q[1]) / ((q[0] - a[0]) + (a[1] - q[1]))       # q beats a only if share >= low
high = (q[1] - b[1]) / ((b[0] - q[0]) + (q[1] - b[1]))      # q beats b only if share <= high
print(f"neighbours a = ({a[0]:,}, {a[1]:,.0f}) and b = ({b[0]:,}, {b[1]:,.0f})")
print(f"beat a: share >= {low:.4f}; beat b: share <= {high:.4f}; both: impossible, {low:.4f} > {high:.4f}")
print(f"the segment a-b at NPV ${q[0]:,}k removes ${q[1] + below_hull(q):,.0f}k; q removes ${q[1]:,.0f}k")
