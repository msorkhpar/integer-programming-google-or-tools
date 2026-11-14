"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import io

import pandas as pd

from budgets import budget_problems

# A three-region, one-year plan. Line 1 of the text is the header.
text = """year,region,budget
2040,Coast,300
2040,Coast,310
2040,Hills,-15
2041,Plain,200
"""
table = pd.read_csv(io.StringIO(text))
for problem in budget_problems(table, [2040], ["Coast", "Hills", "Plain"]):
    print("problem:", problem)
