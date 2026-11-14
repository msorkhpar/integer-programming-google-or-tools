"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import pandas as pd

from entries import hours_entries

options = pd.DataFrame({"task": ["P1", "P2", "P2"], "start": [2, 1, 3]})
profile = pd.DataFrame({"task": ["P1", "P1", "P2", "P2"], "k": [0, 1, 0, 1], "hours": [6, 2, 4, 0]})

table = hours_entries(options, profile, [1, 2, 3])
print("entries for weeks 1 to 3:")
print(table.to_string(index=False))
print("entries for week 3 only:", list(hours_entries(options, profile, [3]).itertuples(index=False, name=None)))
