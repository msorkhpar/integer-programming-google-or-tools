"""Rank GridCap small's assets by PoF, by CoF and by risk: three different top fives."""

from asset_curves import pof_next
from gridcap import generate

small = generate("small")
rows = [(a.asset_id, pof_next(a.age, a.weibull_beta, a.weibull_eta), a.cof) for a in small.assets]


def top(key) -> str:
    return ", ".join(r[0] for r in sorted(rows, key=key, reverse=True)[:5])


print(f"{len(rows)} assets")
print("top 5 by PoF :", top(lambda r: r[1]))
print("top 5 by CoF :", top(lambda r: r[2]))
print("top 5 by risk:", top(lambda r: r[1] * r[2]))
for asset_id, pof, cof in sorted(rows, key=lambda r: r[1] * r[2], reverse=True)[:5]:
    print(f"  {asset_id}: PoF {pof:.4f} x CoF ${cof:,}k = ${pof * cof:,.1f}k per year")


def band(value: float, edges) -> int:
    """A 1-5 score: how many edges the value reaches, plus one."""
    return 1 + sum(value >= e for e in edges)


POF_EDGES, COF_EDGES = (0.01, 0.02, 0.05, 0.10), (500, 1_000, 2_000, 3_000)
cells: dict = {}
for asset_id, pof, cof in rows:
    cells.setdefault((band(pof, POF_EDGES), band(cof, COF_EDGES)), []).append((asset_id, pof * cof))
cell, members = max(cells.items(), key=lambda kv: len(kv[1]))
low, high = min(members, key=lambda m: m[1]), max(members, key=lambda m: m[1])
print(f"busiest risk-matrix cell (PoF band {cell[0]}, CoF band {cell[1]}): {len(members)} assets, "
      f"risk from ${low[1]:,.1f}k ({low[0]}) to ${high[1]:,.1f}k ({high[0]})")
