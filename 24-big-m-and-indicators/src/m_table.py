"""Four ways to get each crew row's big-M on GridCap small, from cheapest to tightest."""

from gridcap import generate
from crew_model import m_by_solving, m_from_once_rows, m_from_variable_bounds

small = generate("small")
bounds = m_from_variable_bounds(small)
once = m_from_once_rows(small)
lp = m_by_solving(small, integer=False)
exact = m_by_solving(small, integer=True)

print("program       year  in-house   M: bounds  once rows  LP max  MILP max")
for (g, y), crews in small.crews.items():
    print(f"{g:13} {y}  {crews:8}   {bounds[g, y]:9}  {once[g, y]:9}  {lp[g, y]:6}  {exact[g, y]:8}")
print("sum of M over the 15 rows:", sum(bounds.values()), sum(once.values()), sum(lp.values()), sum(exact.values()))
