"""The NPV-risk frontier of GridCap small, written for planners: a short table, the price of each step, the knees."""

from frontier import exact_frontier, supported
from gridcap import generate
from objectives import build
from planner import best_reaching, knees, steps

small = generate("small")
two = build(small)
points, _ = exact_frontier(two.model, two.risk, two.npv)       # first = risk removed, second = NPV
hull = supported(points)
npv_end = max(points, key=lambda p: p.second)
base = two.plan(npv_end.values)


def changes(p) -> str:
    """Projects added, dropped and moved to another start year, against the max NPV plan."""
    plan = two.plan(p.values)
    added = len(set(plan) - set(base))
    dropped = len(set(base) - set(plan))
    moved = sum(1 for pid in plan if pid in base and plan[pid] != base[pid])
    return f"+{added} -{dropped} ~{moved}"


bends = knees(hull)
rows = [("max NPV plan", npv_end)] + [(f"best at {t:,}", best_reaching(points, t)) for t in range(11_000, 16_000, 1_000)]
rows += [("knee", p) for p, _, _ in bends] + [("max risk plan", max(points, key=lambda p: p.first))]
shown: dict = {}                                               # one row per plan, its reasons joined
for label, p in rows:
    shown.setdefault(p, []).append(label)
print(f"{len(points)} Pareto-optimal plans; the table shows the ends, the best NPV at each $1,000k of risk, the knees")
print("why shown              | risk removed | NPV    | NPV given up | projects | vs max NPV plan | weighted sum finds it")
for p, labels in sorted(shown.items(), key=lambda item: item[0].first):
    print(f"{', '.join(labels):22} | {p.first:12,.0f} | {p.second:6,.0f} | {npv_end.second - p.second:12,.0f} | "
          f"{len(two.plan(p.values)):8} | {changes(p):>15} | {'yes' if p in hull else 'no'}")

print("\nThe trade-off, step by step along the supported plans:")
for s in steps(hull):
    print(f"  risk {s.a.first:,.0f} -> {s.b.first:,.0f}: +${s.gain:,.0f}k of risk removed for ${s.cost:,.0f}k "
          f"of NPV, ${s.price:.2f} of NPV per $1 of risk")

every = steps(points)
falls = sum(1 for x, y in zip(every, every[1:]) if y.price < x.price)
print(f"Along all {len(points)} plans the {len(every)} steps' prices are not in order: {falls} cost less than the step before")

print("\nThe same steps priced as in lesson 8.1.1, $k of risk removed per $1k of NPV: the reciprocals")
for s in steps(hull):
    print(f"  risk {s.a.first:,.0f} -> {s.b.first:,.0f}: ${s.price:.2f} of NPV per $1 of risk, "
          f"so {1 / s.price:.3f} $k of risk per $1k of NPV")

print("\nKnees (the price at least doubles):")
for p, before, after in bends:
    print(f"  risk ${p.first:,.0f}k, NPV ${p.second:,.0f}k: ${before:.2f} per $1 before, ${after:.2f} after")

worst = max(bends, key=lambda k: k[2] / k[1])[0]
cheap = [s for s in steps(hull) if s.b.first <= worst.first + 1e-6]
dear = [s for s in steps(hull) if s.a.first >= worst.first - 1e-6]
print(f"\nIn one sentence: up to ${worst.first:,.0f}k of risk removed, each extra $1 of risk costs at most "
      f"${max(s.price for s in cheap):.2f} of NPV; beyond it, ${min(s.price for s in dear):.2f} to "
      f"${max(s.price for s in dear):.2f}.")
