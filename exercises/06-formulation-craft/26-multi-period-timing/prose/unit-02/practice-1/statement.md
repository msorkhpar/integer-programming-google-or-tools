Three counties fund a shared fiber-backbone program, and each county's board approves its own
yearly cap. The plan's model must report, for every county and every year, what the plan spends
there, so a cap can be written against each number.

Write `spend_by_region_year(projects, x, years)` in `regional.py`. It returns a dict with one entry
for every `(region, year)` pair (every region that has a project, every year in `years`), each a
linear expression in the start variables `x[(pid, start_year)]`. A project's `cost_profile[k]` is
what it spends in its k-th year of work, counting its start year as year 0. A cost that would fall in a
year outside `years` belongs to no entry.

The tests fix a schedule and evaluate your expressions, so any correct expression passes. About
eight lines in total.


In the lesson's notation, with $`R`$ the regions, $`P_r`$ the projects in region $`r`$, $`T_i`$
the start years of project $`i`$, $`c_{i,k}`$ its `cost_profile[k]` and $`x_{i,t} \in \{0, 1\}`$
the start variables, you are writing the expression $`\text{spend}_{r,y}`$ for every
$`r \in R`$ and $`y \in Y`$. Write it as a sum first (which pairs $`(i, t)`$ put money into year
$`y`$?), then code it. A cap would then be the row $`\text{spend}_{r,y} \le \text{cap}_{r,y}`$.
