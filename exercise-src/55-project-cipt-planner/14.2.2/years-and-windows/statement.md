Finance read the first plan and sent it back:

> Your plan spends $13.14M in 2027. We have $8.89M that year. The $38.39M was five yearly budgets
> added up, and they are not interchangeable: money not spent in a year does not roll over. Plan
> by year. A project may start in any year of its window, and its cost lands in the years it is
> worked on, not all at the start. And no plan may run past 2031.

You start from the one-envelope planner of the lesson before. Change it to plan by year. Read each
project's cost profile and latest start and each year's budget from the export, and let the model
choose the year each funded project starts, inside its window. A project's cost is spent over its
years of work, and each year's spend stays within that year's budget. No project may be funded with
work that runs past the plan's last year. The plan says the year each funded project starts, and
the report shows each year's spend against its budget.

`Request.starts` is a stub in `cipt/data.py` that returns the earliest year alone; `Project` needs
the arithmetic of its profile too: how many years its work lasts, and what it spends in each
calendar year for a given start. The report keeps its status line and its project lines and
changes in two ways, every amount in whole $k with thousands commas:

- the funded line's budget is the total of all yearly budgets:
  `funded <n> of <all> projects, capex $<capex>k of $<sum of yearly budgets>k, value $<value>k`,
  where value is still the funded projects' earliest-start value;
- after it, before the project lines, one line per plan year in year order:
  `  <year>  spend $<spend>k of $<budget>k` (two spaces before the year and two after it), with
  0 for a year nothing spends in.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.
