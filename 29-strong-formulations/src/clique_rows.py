"""Conflicts between starts of GridCap small, written as pair rows and as clique rows."""

from gridcap import generate
import itertools

from derived_rows import already_a_row, cliques, conflict_reasons, fixable
from strong_model import EXACT, build, lp_bound, root_bound, solve_highs

small = generate("small")
fixed = fixable(small)
reasons = conflict_reasons(small, fixed)
pairs = set(reasons)
new_pairs = sorted(sorted(p) for p in pairs if not already_a_row(sorted(p), small))
found = cliques(pairs)
new_cliques = [c for c in found if not already_a_row(c, small)]
print(f"conflicting pairs {len(pairs)}, of them not already in one once or alt row {len(new_pairs)}")
print(f"cliques covering every conflict {len(found)}, of them new rows {len(new_cliques)}; sizes "
      f"{sorted((len(c) for c in new_cliques), reverse=True)}")
mixed = max((c for c in new_cliques if len({pid for pid, _ in c}) < len(c)), key=len)
print("the widest that repeats a project:", " + ".join(f"x[{pid},{t}]" for pid, t in mixed), "<= 1")
for u, v in itertools.combinations(mixed, 2):
    print(f"  x[{u[0]},{u[1]}] and x[{v[0]},{v[1]}]: {reasons[frozenset((u, v))]}")

def model(rows: str, integer: bool):
    sm = build(small, integer=integer, fronts=None, crews=True)
    for start in fixed:
        sm.x[start].upper_bound = 0
    groups = new_pairs if rows == "pairs" else new_cliques if rows == "cliques" else []
    for n, group in enumerate(groups):
        sm.model.add_linear_constraint(sum(sm.x[s] for s in group) <= 1, name=f"{rows}_{n}")
    return sm.model


base_rows = sum(1 for _ in model("none", integer=True).linear_constraints())
for rows in ("none", "pairs", "cliques"):
    lp = lp_bound(model(rows, integer=False)).objective_value()
    milp = model(rows, integer=True)
    print(f"fixings + {rows:7}  rows added {sum(1 for _ in milp.linear_constraints()) - base_rows:3}  "
          f"LP bound {lp:,.2f}  HiGHS root bound {root_bound(milp):,.0f}  MILP {solve_highs(milp, EXACT).objective_value():,.0f}")
