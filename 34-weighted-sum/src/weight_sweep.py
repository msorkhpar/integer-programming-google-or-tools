"""Sweep the share of weight on NPV from 0 to 1 and watch the plan jump between a few plans."""

from gridcap import generate
from two_objectives import build, score, weighted

small = generate("small")
sm = build(small)

found = {}                                    # (NPV, risk) -> (shares that picked it, plan)
for k in range(101):
    share = k / 100                           # weight on NPV; risk gets the rest
    plan = weighted(sm, share, 1 - share)
    npv, risk = score(sm, plan)
    found.setdefault((npv, round(risk, 6)), ([], plan))[0].append(share)

print(f"101 weightings, {len(found)} different plans")
print("NPV share  |   NPV $k | risk removed $k | projects")
for (npv, risk), (shares, plan) in found.items():
    print(f"{min(shares):.2f}-{max(shares):.2f}  | {npv:8,} | {risk:15,.0f} | {len(plan)}")

print("break-even between neighbours: price = risk given up / NPV gained, share = price / (1 + price)")
points = list(found)
for (n1, r1), (n2, r2) in zip(points, points[1:]):
    price = (r1 - r2) / (n2 - n1)
    print(f"  {n1:,} -> {n2:,}: gain ${n2 - n1:,}k NPV for ${r1 - r2:,.0f}k risk, "
          f"price {price:.3f}, share {price / (1 + price):.4f}")

a, b = found[points[2]][1], found[points[3]][1]
kept = sorted(p for p in a if p in b and a[p] == b[p])
moved = sorted(p for p in a if p in b and a[p] != b[p])
print(f"{points[2][0]:,} -> {points[3][0]:,}: {len(kept)} projects kept, {len(moved)} moved to another year, "
      f"dropped {sorted(set(a) - set(b))}, added {sorted(set(b) - set(a))}")
