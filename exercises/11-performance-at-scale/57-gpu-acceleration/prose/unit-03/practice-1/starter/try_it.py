"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from routes import build, solve

supply, demand = [10.0, 6.0], [5.0, 7.0]
cost = [[2.0, 5.0], [4.0, 1.0]]
loose = [[50.0, 50.0], [50.0, 50.0]]

lp = build(supply, demand, cost, loose)
print("columns, rows:", lp.num_col_, lp.num_row_)
print("column starts:", list(lp.a_matrix_.start_), "row indices:", list(lp.a_matrix_.index_))
print("loose caps:", solve(lp, "ipm"))
print("route 1 -> 1 capped at 2:", solve(build(supply, demand, cost, [[50.0, 50.0], [50.0, 2.0]]), "simplex"))
print("demand 20 at customer 1:", solve(build(supply, [5.0, 20.0], cost, loose), "ipm")[0])
