"""The whole HiGHS log of the five-year selection model on GridCap medium, as the solver wrote it."""

from gridcap import generate
from selection import five_year, solve_with_log

result, log = solve_with_log(five_year(generate("medium")).model)
for line in log:
    print(line)
