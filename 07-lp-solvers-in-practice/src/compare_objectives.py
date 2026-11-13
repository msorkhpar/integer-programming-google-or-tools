"""The same LP on GLOP, HiGHS and PDLP (GridCap large): equal objectives, within a relative tolerance."""

from ortools.math_opt.python import mathopt

from funding_lp import build, in_between
from gridcap import generate

large = generate("large")
lp = build(large)
print(f"funding LP on large: {len(lp.f)} projects, {len(lp.must)} must-do, {len(lp.cash)} years")

objective = {}
for solver in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP):
    result = mathopt.solve(lp.model, solver)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise SystemExit(f"{solver.name}: {result.termination.reason.name}")
    objective[solver.name] = result.objective_value()
    print(f"{solver.name:5} objective {result.objective_value():,.4f}  in-between {in_between(lp, result)}")


def relative_gap(a: float, b: float) -> float:
    """|a - b| measured against the larger magnitude, never against less than 1."""
    return abs(a - b) / max(1.0, abs(a), abs(b))


for a, b in (("GLOP", "HIGHS"), ("GLOP", "PDLP")):
    gap = relative_gap(objective[a], objective[b])
    print(f"{a} vs {b}: equal? {objective[a] == objective[b]}  difference {abs(objective[a] - objective[b]):.6f}"
          f"  relative {gap:.1e}  within 1e-6? {gap <= 1e-6}")
