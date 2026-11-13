A rail operator's maintenance planner gets "conflicts" from three tools: its own filter, a
commercial solver's IIS, and a library that works on the LP relaxation. Before a conflict goes to
the track engineers, the planner wants it audited against the model the engineers actually use.

You get the claimed conflict, a list of rule names, and an oracle, `infeasible(rules) -> bool`,
which answers for the real model (integers included) with exactly the rules in `rules` switched
on. Write `audit(claim, infeasible)` returning a dict with two keys:

- `"infeasible"`: whether the claimed rules, all switched on, really have no solution;
- `"not_needed"`: the members of the claim, in the claim's order, that could each be switched off
  while the rest of the claim stays infeasible. An irreducible conflict has none. When the claim is
  not infeasible at all, this list is empty.

Test each member against the rest of the claim with only that one member removed. About six lines.
