"""Lesson 6.6.3: the falling-tier credit line written three ways, compared by size, MILP and LP bound.

GridCap is a fictional utility's portfolio; the credit line is invented (lesson 6.6.1). The LP
bound is the optimum with every integer variable relaxed to its interval, the project binaries
and the curve's binaries alike.
"""

from credit_exact import weights_only
from credit_line import FALLING, with_credit
from gridcap import generate
from piecewise import FORMS, value
from selection import EXACT, solve_highs


def relax(model):
    for v in model.variables():
        v.integer = False


if __name__ == "__main__":
    small = generate("small")
    print("form        | curve binaries | rows | MILP      | LP bound   | drawn")
    for name, form in FORMS.items():
        sel, loan = with_credit(small, FALLING, form)
        rows = sel.model.get_num_linear_constraints()
        milp = solve_highs(sel.model, EXACT)
        relax(sel.model)
        lp = solve_highs(sel.model)
        print(f"{name:11} | {len(loan.binaries):14} | {rows:4} | ${milp.objective_value():,.0f}k | "
              f"${lp.objective_value():,.1f}k | ${value(milp, loan.x):,.0f}k")
    sel, loan = with_credit(small, FALLING, weights_only)
    relax(sel.model)
    print(f"LP bound with weights only, no curve binaries at all: ${solve_highs(sel.model).objective_value():,.1f}k")
    sel, loan = with_credit(small, FALLING, FORMS["incremental"])
    milp = solve_highs(sel.model, EXACT)
    print("incremental fills", [round(milp.variable_values(v), 3) for v in loan.parts["fill"]],
          "full", [round(milp.variable_values(v)) for v in loan.binaries])
