A hospital builds its nurse rosters with a MIP that minimizes cost, and its scheduling team wants to
know whether starting each solve from last month's roster helps. For each run the solver's
callback records an event $`(w_k, z_k)`$ every time it reports a plan: $`w_k`$ is its
deterministic work at that moment and $`z_k`$ the plan's cost. The events come in the order found,
and a solver may report a plan that is no better than one it already had.

Before you code, write each measure in this notation, for a run with events
$`(w_1, z_1), \dots, (w_n, z_n)`$:

- the work to the first plan;
- the work until a plan within a share $`\sigma`$ of the best known cost $`z^*`$ was found (say
  what "within" means as an inequality on $`z_k`$, for any sign of $`z^*`$);
- the plan in hand after $`W`$ units of work: the cost of the best plan found by then.

Write `work_to_first(events)`, `work_to_within(events, best, share)` and `in_hand(events, budget)` in
`incumbents.py`. A measure with no plan to report is `math.inf` for work and `None` for a cost.
The tests pass small event lists; no solver runs. About six lines.
