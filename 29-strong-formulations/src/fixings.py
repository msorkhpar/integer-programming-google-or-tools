"""Starts that no whole plan can use, found from the crew and budget rows of GridCap small."""

from gridcap import generate
from derived_rows import capacity_rows, fixable, room
from strong_model import EXACT, build, lp_bound, solve_highs

small = generate("small")
rows = {row.name: row for row in capacity_rows(small)}
fixed = fixable(small)


def before(round_):
    """The starts fixed in earlier rounds: what the round that fixed a start knew."""
    return {s: v for s, v in fixed.items() if v[0] < round_}


print(f"{len(fixed)} of {sum(len(p.starts()) for p in small.projects)} starts can be fixed at 0:")
for (pid, t), (round_, name) in sorted(fixed.items(), key=lambda kv: (kv[1][0], kv[0])):
    row = rows[name]
    must = " (must-do)" if small.project(pid).must_do else ""
    print(f"  round {round_}: {pid}{must} starting {t}: needs {row.use[pid, t]} of {name} ({row.capacity}), and the must-dos leave {room(small, row, before(round_))}")

for label, fix in (("as written", False), ("starts fixed", True)):
    lp = build(small, integer=False, fronts=None, crews=True)
    milp = build(small, fronts=None, crews=True)
    if fix:
        for start in fixed:
            lp.x[start].upper_bound = 0
            milp.x[start].upper_bound = 0
    print(f"{label:12}  LP bound {lp_bound(lp.model).objective_value():,.2f}  "
          f"MILP {solve_highs(milp.model, EXACT).objective_value():,.0f}")
