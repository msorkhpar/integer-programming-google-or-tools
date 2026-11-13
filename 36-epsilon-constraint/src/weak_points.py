"""When finance books vegetation work at NPV 0, plain ε-constraint returns weakly efficient plans; AUGMECON does not."""

from dataclasses import replace

from frontier import augmecon, dominates, epsilon_constraint, grid, payoff_table
from gridcap import generate
from objectives import build

small = generate("small")
# A variant made for this lesson: every vegetation project's NPV is 0 (no revenue, compliance work).
zero_veg = replace(small, projects=tuple(
    replace(p, npv={s: 0 for s in p.npv}) if p.program == "vegetation" else p for p in small.projects))
two = build(zero_veg)
print(f"vegetation projects booked at NPV 0: {sum(p.program == 'vegetation' for p in zero_veg.projects)}")

for lexicographic in (False, True):
    a, b = payoff_table(two.model, two.npv, two.risk, lexicographic=lexicographic)
    print(f"payoff table, {'lexicographic' if lexicographic else 'one pass    '}: max NPV end ({a.first:,.0f}, "
          f"{a.second:,.0f}), max risk end ({b.first:,.0f}, {b.second:,.0f})")

span = b.second - a.second                                    # the range of risk over the payoff table
print("risk floor |  plain: NPV, risk  | AUGMECON: NPV, risk | plain is")
weak = 0
for floor in grid(a.second, b.second, 11):
    p = epsilon_constraint(two.model, two.npv, two.risk, floor)
    q, slack = augmecon(two.model, two.npv, two.risk, floor, span)
    verdict = "weakly efficient" if dominates(q, p) else "Pareto-optimal"
    weak += dominates(q, p)
    print(f"{floor:10,.0f} | {p.first:7,.0f} {p.second:9,.0f}  | {q.first:7,.0f} {q.second:9,.0f}   | {verdict}")
print(f"plain ε-constraint returned {weak} weakly efficient plans out of 11")
