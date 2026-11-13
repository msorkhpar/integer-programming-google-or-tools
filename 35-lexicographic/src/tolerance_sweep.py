"""What a relative and an absolute NPV tolerance buy in risk removed, measured on GridCap small."""

from gridcap import generate
from lex_model import build, score
from lexicographic import Level, allowed_loss, solve_levels

small = generate("small")
sm = build(small)
base = solve_levels(sm, [Level("npv"), Level("risk")])
best, risk0 = base.best["npv"], score(sm, base.plan, "risk")


def row(label: str, first: Level) -> None:
    plan = solve_levels(sm, [first, Level("risk")]).plan
    npv, risk = score(sm, plan, "npv"), score(sm, plan, "risk")
    print(f"{label:>9} {allowed_loss(best, first):8,.1f} {best - npv:6,.0f} {npv:8,.0f} {risk:9,.1f} {risk - risk0:+8,.1f}")


print("tolerance  allowed  taken      NPV      risk   gained")
for rel in (0.0, 0.001, 0.0025, 0.005, 0.01, 0.02, 0.05, 0.10):
    row(f"{rel:.2%}", Level("npv", rel_tol=rel))
for absolute in (10, 50, 100, 242.6, 500, 1000):
    row(f"${absolute:,g}k", Level("npv", abs_tol=absolute))
