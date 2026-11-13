"""Check every derived row against every whole plan of GridCap tiny, by brute force."""

import itertools

from gridcap import generate
from derived_rows import cliques, conflicts, fixable
from strong_model import build

tiny = generate("tiny")
sm = build(tiny, fronts=None, crews=True)
starts = list(sm.x)
rows = [(c.lower_bound, {t.variable: t.coefficient for t in c.terms()}, c.upper_bound)
        for c in sm.model.linear_constraints()]


def allowed(plan: dict) -> bool:
    """Does the 0/1 point satisfy every row of the model?"""
    for low, terms, high in rows:
        activity = sum(a * plan[v] for v, a in terms.items())
        if not low - 1e-9 <= activity <= high + 1e-9:
            return False
    return True


fixed = fixable(tiny)
groups = cliques(conflicts(tiny, fixed))
plans = []
for values in itertools.product((0, 1), repeat=len(starts)):
    if allowed({sm.x[s]: v for s, v in zip(starts, values)}):
        plans.append(dict(zip(starts, values)))
broken = sum(any(plan[s] for s in fixed) + sum(sum(plan[s] for s in g) > 1 for g in groups) for plan in plans)
print(f"{len(starts)} start variables, {2 ** len(starts)} 0/1 points, {len(plans)} of them allowed plans")
print(f"derived: {len(fixed)} fixings, {len(groups)} clique rows; broken by an allowed plan: {broken}")

# The same check catches a wrong row: two starts some allowed plan uses together, claimed to conflict.
u, v = next((u, v) for u, v in itertools.combinations(starts, 2) if any(p[u] and p[v] for p in plans))
wrong = sum(1 for p in plans if p[u] + p[v] > 1)
print(f"planted row x[{u[0]},{u[1]}] + x[{v[0]},{v[1]}] <= 1 is broken by {wrong} allowed plans")
