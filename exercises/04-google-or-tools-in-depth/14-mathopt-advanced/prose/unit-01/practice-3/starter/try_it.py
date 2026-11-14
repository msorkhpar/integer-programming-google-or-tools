"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from fallback import solve_first

S = mathopt.SolverType

# A cold room: when the chiller is off, the stock held is at most 15.
model = mathopt.Model(name="cold-room")
chiller = model.add_binary_variable(name="chiller")
stock = model.add_variable(lb=0, ub=70, name="stock")
model.add_indicator_constraint(indicator=chiller, activate_on_zero=True, implied_constraint=stock <= 15)
model.maximize(stock - 40 * chiller)

for order in ([S.HIGHS, S.GSCIP], [S.GSCIP, S.HIGHS], [S.CP_SAT, S.GLOP]):
    solver, result, reasons = solve_first(model, order)
    names = [s.name for s in order]
    print(f"order {names}: solver", solver and solver.name,
          "value", result and round(result.objective_value(), 3))
    print(f"  refusals for {names}:", {k: v[:70] for k, v in reasons.items()})
