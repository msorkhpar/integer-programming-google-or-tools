This is the mock's whiteboard, coded. A transit agency's must-do projects no longer fit its yearly
budgets, and finance can cover an overspend in any year at a price per $k that differs by year.
`elastic.py` already has a binary `x[pid]` per project and the hard rows that fund every must-do;
each project spends its whole `cost` in its `year`.

Write `add_elastic_budgets(model, x, projects, budgets, penalty)` so that solving the model gives
the cheapest overspend: each year's spend may exceed `budgets[year]`, the excess costs
`penalty[year]` per $k, and the model minimizes the total. Finance covers any amount, so a year's
overspend is a continuous variable, at least 0, with no upper bound: it may exceed the year's own
budget. Solved with a plan fixed, the same model
must give that plan's overspend cost. Write the formulation first: the new variables with their
domains, the elastic rows with labels, and the objective.

The tests fix plans or leave them free and compare the optimal penalty with the arithmetic, so any
correct formulation passes. About six lines.
