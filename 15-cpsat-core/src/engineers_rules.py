"""Lesson 4.4.2: the engineers' rules of lesson 6.1.2 and an all-or-nothing bundle, each one CP-SAT constraint.

GridCap is a fictional utility's portfolio, and these rules are invented for the course. Each rule
is also written as the linear row of lesson 6.1.2 in MathOpt, and HiGHS solves that model, so the
two objectives can be compared.
"""

from cpsat_models import EXACT, funded, mathopt_selection, one_worker, selection, solve_highs
from gridcap import generate

small = generate("small")

# Each rule: (name, its CP-SAT constraint, its linear row from lesson 6.1.2 for MathOpt)
RULES = [
    ("conflict", lambda m, x: m.add_at_most_one(x["P030"], x["P032"]),
     lambda m, x: m.add_linear_constraint(x["P030"] + x["P032"] <= 1)),
    ("needs", lambda m, x: m.add_implication(x["P028"], x["P024"]),
     lambda m, x: m.add_linear_constraint(x["P028"] <= x["P024"])),
    ("both_need", lambda m, x: m.add_bool_or(~x["P022"], ~x["P025"], x["P033"]),
     lambda m, x: m.add_linear_constraint(x["P022"] + x["P025"] - 1 <= x["P033"])),
    ("needs_one", lambda m, x: m.add_bool_or(x["P013"], x["P040"]).only_enforce_if(x["P034"]),
     lambda m, x: m.add_linear_constraint(x["P034"] <= x["P013"] + x["P040"])),
    ("bundle", lambda m, x: m.add(x["P019"] == x["P024"]),
     lambda m, x: m.add_linear_constraint(x["P019"] == x["P024"])),
]


def solve(rules) -> tuple[str, int, list[str], float]:
    sel = selection(small, native=True)
    for _, cp_rule, _ in rules:
        cp_rule(sel.model, sel.x)
    solver = one_worker()
    status = solver.solve(sel.model)
    model, x, _ = mathopt_selection(small)
    for _, _, linear_row in rules:
        linear_row(model, x)
    highs = solve_highs(model, EXACT).objective_value()
    return solver.status_name(status), round(solver.objective_value), funded(sel, solver), highs


status0, npv0, plan0, _ = solve([])
print(f"no extra rule  {status0}  objective {npv0:,}")
for rule in RULES:
    status, npv, plan, highs = solve([rule])
    print(f"{rule[0]:14} {status}  objective {npv:,} ({npv - npv0:+,})  HiGHS {highs:,.0f}"
          f"  adds {sorted(set(plan) - set(plan0))}  drops {sorted(set(plan0) - set(plan))}")
status, npv, plan, highs = solve(RULES)
print(f"{'all five':14} {status}  objective {npv:,} ({npv - npv0:+,})  HiGHS {highs:,.0f}"
      f"  adds {sorted(set(plan) - set(plan0))}  drops {sorted(set(plan0) - set(plan))}")
