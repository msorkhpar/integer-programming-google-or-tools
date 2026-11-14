"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import pandas as pd

from inspections import build_fast, build_slow, instance

tasks = pd.DataFrame({"task": ["V1", "V2", "V3"], "hours": [10, 6, 14], "value": [25, 15, 40]})
options = pd.DataFrame({"task": ["V1", "V2", "V2", "V3"], "week": [1, 1, 2, 2]})
capacity = pd.DataFrame({"week": [2, 1, 3], "hours": [18, 12, 9]})

fast = build_fast(tasks, options, capacity)
print("variables, three tasks:", fast.get_num_variables())
print("rows, three tasks:", fast.get_num_linear_constraints())
print("same as slow, three tasks:", fast.export_model() == build_slow(tasks, options, capacity).export_model())

tasks, options, capacity = instance(60, seed=7)
print("same as slow, 60 made-up tasks:",
      build_fast(tasks, options, capacity).export_model() == build_slow(tasks, options, capacity).export_model())
