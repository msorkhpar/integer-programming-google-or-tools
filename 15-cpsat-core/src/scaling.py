"""Lesson 4.4.3: fractional data in CP-SAT: rows scaled exactly, objectives scaled within a tolerance.

GridCap is a fictional utility's portfolio. The objective is the expected number of asset failures
over the next five years that a plan avoids: each funded project's asset contributes its
probability of failing in that time, from its Weibull curve, given its age.
"""

import itertools
import math
from fractions import Fraction

from gridcap import generate
from cpsat_models import EXACT, mathopt_selection, one_worker, selection, solve_highs


def scale_row(coefficients: list[str], rhs: str) -> tuple[int, list[int], int]:
    """sum c_j x_j <= rhs with decimal data -> (multiplier, whole coefficients, whole rhs), same 0/1 plans."""
    exact = [Fraction(c) for c in coefficients]
    multiplier = math.lcm(*(f.denominator for f in exact))
    whole = [int(f * multiplier) for f in exact]
    return multiplier, whole, math.floor(Fraction(rhs) * multiplier)  # whole left side: round the bound down


def plans(coefficients, rhs) -> set[tuple[int, ...]]:
    return {xs for xs in itertools.product((0, 1), repeat=len(coefficients))
            if sum(Fraction(c) * x for c, x in zip(coefficients, xs)) <= Fraction(rhs)}


need, capacity = ["1.5", "2.5", "0.75", "3.5", "2.5"], "7.6"      # crew-months; a crew row
m, whole, rhs = scale_row(need, capacity)
print(f"row  {' + '.join(f'{c} x{j}' for j, c in enumerate(need))} <= {capacity}")
print(f"x{m}  {' + '.join(f'{c} x{j}' for j, c in enumerate(whole))} <= {rhs}")
print("same 0/1 plans:", plans(need, capacity) == plans([str(c) for c in whole], str(rhs)))
rounded = [str(round(Fraction(c))) for c in need]
print(f"rounded coefficients {rounded}: same 0/1 plans:", plans(need, capacity) == plans(rounded, capacity))

small = generate("small")


def pof(project) -> float:
    """Probability that the project's asset fails in the next 5 years, given that it is working now."""
    a = small.asset(project.asset_id)
    F = lambda t: 1 - math.exp(-((t / a.weibull_eta) ** a.weibull_beta))
    return (F(a.age + 5) - F(a.age)) / (1 - F(a.age))


avoided = {p.project_id: pof(p) for p in small.projects}
print("five-year failure probabilities:", ", ".join(f"{p} {v:.4f}" for p, v in list(avoided.items())[:4]), "...")

model, x, k = mathopt_selection(small)
model.add_linear_constraint(k == 0)
model.maximize(sum(avoided[i] * x[i] for i in x))
best = solve_highs(model, EXACT).objective_value()
print(f"HiGHS, float objective: {best:.4f} failures avoided")

for scale in (None, 1, 10, 100, 1000):
    sel = selection(small, native=True)
    sel.model.add(sel.k == 0)                                 # no borrowing in this comparison
    if scale is None:
        sel.model.maximize(sum(avoided[i] * v for i, v in sel.x.items()))
    else:
        sel.model.maximize(sum(round(scale * avoided[i]) * v for i, v in sel.x.items()))
    solver = one_worker()
    status = solver.solve(sel.model)
    true = sum(avoided[i] for i, v in sel.x.items() if solver.boolean_value(v))
    label = "floats as given" if scale is None else f"x{scale}, rounded"
    print(f"CP-SAT {label:16} {solver.status_name(status)}  objective {solver.objective_value:>10,.4f}"
          f"  true value {true:.4f}  short by {best - true:.4f}")
