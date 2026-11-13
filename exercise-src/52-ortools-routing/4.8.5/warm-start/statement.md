A bakery's dispatcher reuses yesterday's van routes as the starting point for today's, because the
drivers know them. Sometimes they no longer fit: a van is in the workshop and the spare is smaller.
Write `replan(routing, yesterday, params)` in `warm.py`. `yesterday` holds one list of cafe nodes
per van, depot left out. Return a pair:

- yesterday's cost under today's model, or `None` when yesterday's routes break one of today's
  rules;
- today's solution: searched from yesterday's routes when they fit, solved from scratch when they
  do not.

The model is the one `build` makes and does not change: routes priced by distance, with the
capacity rule $`\text{load}_i \le K_v`$ on every van. What changes is where the search starts.
Before you code, say which call must come before reading the routes when you search with your own
parameters, and what reading the routes returns for a plan the model refuses.

The tests compare costs, so any correct order of calls passes. About five lines.
