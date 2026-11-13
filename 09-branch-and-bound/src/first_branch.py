"""Lesson 3.2.1: branch the tiny relaxation on x_P003. Every allowed plan lands in exactly one child."""

from itertools import product

from gridcap import generate
from selection import build, solve_lp

tiny = generate("tiny")
ids = [p.project_id for p in tiny.projects]


def allowed(x: dict[str, int]) -> bool:
    """The model's rows, checked on a 0-1 plan."""
    if sum(tiny.project(i).capex * x[i] for i in ids) > tiny.capital_budget:
        return False
    if any(p.must_do and x[p.project_id] == 0 for p in tiny.projects):
        return False
    if any(p.parent and x[p.project_id] > x[p.parent] for p in tiny.projects):
        return False
    return x["P006"] + x["P007"] <= 1


def value(x: dict[str, int]) -> int:
    return sum(tiny.project(i).value * x[i] for i in ids)


plans = [dict(zip(ids, bits)) for bits in product((0, 1), repeat=len(ids))]
good = [x for x in plans if allowed(x)]
down = [x for x in good if x["P003"] == 0]
up = [x for x in good if x["P003"] == 1]
print(f"allowed plans: {len(good)} = {len(down)} with x_P003 = 0 + {len(up)} with x_P003 = 1")
print(f"best plan with x_P003 = 0: {max(map(value, down)):,}; with x_P003 = 1: {max(map(value, up)):,}")

sel = build(tiny)
for name, fixed in (("down child, x_P003 = 0", {"P003": 0}), ("up child,   x_P003 = 1", {"P003": 1})):
    lp = solve_lp(sel, fixed)
    shown = ", ".join(f"{pid} {v:.3f}" for pid, v in lp.x.items() if v > 1e-9)
    print(f"{name}: LP {lp.value:,.1f}  [{shown}]")
