"""Three plans, pick one: a Pareto-optimal plan that no weighted sum ever picks."""

plans = {"A": (10, 1), "B": (1, 10), "C": (5, 5)}       # (objective 1, objective 2), both maximized


def dominates(p, q) -> bool:
    """p is at least as good as q in both objectives and better in one."""
    return p[0] >= q[0] and p[1] >= q[1] and p != q


for name, q in plans.items():
    beaten = [o for o, p in plans.items() if dominates(p, q)]
    print(f"{name} {q}: dominated by {beaten or 'nothing'}")

print("share on objective 1 -> weighted scores of A, B, C -> pick")
for k in range(11):
    s = k / 10
    scores = {name: s * a + (1 - s) * b for name, (a, b) in plans.items()}
    pick = max(scores, key=scores.get)
    print(f"  {s:.1f}: " + "  ".join(f"{n} {v:4.1f}" for n, v in scores.items()) + f"  -> {pick}")

half = tuple((a + b) / 2 for a, b in zip(plans["A"], plans["B"]))
print(f"half of A plus half of B: {half}, which dominates C: {dominates(half, plans['C'])}")
