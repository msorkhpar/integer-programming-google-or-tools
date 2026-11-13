"""GridCap small: each objective alone, and the two lexicographic orders with no tolerance."""

from gridcap import generate
from lex_model import build, score
from lexicographic import Level, solve_levels

small = generate("small")
sm = build(small)

runs = {
    "NPV alone":                [Level("npv")],
    "NPV, then risk":           [Level("npv"), Level("risk")],
    "risk alone":               [Level("risk")],
    "risk, then NPV":           [Level("risk"), Level("npv")],
    "risk within 1%, then NPV": [Level("risk", rel_tol=0.01), Level("npv")],
}
for label, levels in runs.items():
    plan = solve_levels(sm, levels).plan
    print(f"{label:25} NPV ${score(sm, plan, 'npv'):7,.0f}k  risk removed ${score(sm, plan, 'risk'):7,.1f}k"
          f"  projects {len(plan)}")
