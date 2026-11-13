"""A huge M lets the solver's integrality tolerance switch a rule off without paying for it."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from crew_model import build, hired, m_by_solving, quiet_solve

small = generate("small")
tight = m_by_solving(small, integer=True)
no_presolve = mathopt.SolveParameters(presolve=mathopt.Emphasis.OFF)

for name, big_m in (("MILP max", tight), ("1e6", 1e6), ("1e7", 1e7), ("1e9", 1e9)):
    cm = build(small, big_m)
    result = quiet_solve(cm.model, params=no_presolve)
    values = result.variable_values()
    print(f"M = {name:8} {result.termination.reason.name}  objective {result.objective_value():9,.1f}"
          f"  contractors hired {len(hired(cm, result))}")
    for key, hire in cm.hire.items():
        over = mathopt.evaluate_expression(cm.use[key], values) - small.crews[key]
        if values[hire] < 0.5 and over > 1e-6:
            print(f"    {key[0]:12} {key[1]}  {over:4.1f} crew-months over, hire = {values[hire]:.1e}"
                  f"  (M x hire = {cm.big_m[key] * values[hire]:.1f})")

cm = build(small, 1e9)
result = quiet_solve(cm.model)
print(f"M = 1e9 with presolve on (the default): objective {result.objective_value():,.1f}"
      f"  contractors hired {len(hired(cm, result))}")
print(f"crew-row coefficients: crew-months {min(p.crew_months for p in small.projects)} to "
      f"{max(p.crew_months for p in small.projects)}, tight M up to {max(tight.values())}, loose M 1e9")
