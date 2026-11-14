"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import pandas as pd
from ortools.math_opt.python import mathopt

from selection import solve_selection

S = mathopt.SolverType
courts = pd.DataFrame({
    "project_id": ["Lark", "Wren", "Kite", "Rook", "Tern"],
    "cost": [30, 22, 45, 18, 26],
    "value": [41, 27, 58, 20, 33],
    "must_do": [False, False, False, True, False],
})

for solver in (S.HIGHS, S.GSCIP, S.CP_SAT):
    print(f"budget 90 on {solver.name}:", solve_selection(courts, 90, solver))
print("budget 60 on HIGHS:", solve_selection(courts, 60, S.HIGHS))
