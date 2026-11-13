"""Lesson 6.6.2: the falling-tier credit line of lesson 6.6.1, solved exactly with the lambda form.

GridCap is a fictional utility's portfolio; the credit line is invented. The program solves the
selection model with the credit line's cost written as weights only, then as weights with one
binary per segment, and prints the weights each solve chose.
"""

from credit_line import FALLING, with_credit
from gridcap import generate
from piecewise import add_lambda, value
from selection import EXACT, funded, solve_highs


def weights_only(model, curve, name):
    return add_lambda(model, curve, name, binaries=False)


if __name__ == "__main__":
    small = generate("small")
    for label, form in (("weights only          ", weights_only), ("weights + seg binaries", add_lambda)):
        sel, loan = with_credit(small, FALLING, form)
        result = solve_highs(sel.model, EXACT)
        drawn = value(result, loan.x)
        npv = sum(small.project(i).value for i in funded(sel, result))
        lam = [round(result.variable_values(v), 3) for v in loan.parts["lam"]]
        print(f"{label}: objective ${result.objective_value():,.0f}k, drawn ${drawn:,.0f}k, weights {lam}")
        print(f"{'':24}cost charged ${npv - result.objective_value():,.0f}k, real cost ${FALLING(drawn):,.0f}k, "
              f"plan really worth ${npv - FALLING(drawn):,.0f}k")
        if loan.binaries:
            print(f"{'':24}segment binaries {[round(result.variable_values(v)) for v in loan.binaries]}")

    print("the board must approve any draw from the last tier (above $3,000k); approval costs $A k")
    for approval in (200, 500, 800):
        sel, loan = with_credit(small, FALLING, add_lambda)
        board = sel.model.add_binary_variable(name="board")
        sel.model.add_linear_constraint(board >= loan.binaries[2], name="needs_board")
        sel.model.maximize(sel.model.objective.as_linear_expression() - approval * board)
        result = solve_highs(sel.model, EXACT)
        print(f"  A = {approval}: objective ${result.objective_value():,.0f}k, drawn ${value(result, loan.x):,.0f}k, "
              f"segment binaries {[round(result.variable_values(v)) for v in loan.binaries]}, "
              f"board {round(result.variable_values(board))}")
