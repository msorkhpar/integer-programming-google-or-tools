"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from matrices import needs_matrix, spend_matrix

# (id, start year, spend per year of the project)
projects = [("reservoir", 2050, [600.0, 200.0]), ("filter", 2051, [150.0]), ("tunnel", 2052, [90.0, 90.0])]
years = [2050, 2051, 2052]
print("spend matrix, years 2050-2052:")
print(spend_matrix(projects, years))
print("needs matrix, filter needs reservoir, tunnel needs filter:")
print(needs_matrix(projects, {"filter": "reservoir", "tunnel": "filter"}))
