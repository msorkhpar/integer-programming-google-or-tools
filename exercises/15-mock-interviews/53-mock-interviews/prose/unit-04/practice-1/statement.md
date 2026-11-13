A planning service must tell planners which of a failed scenario's rules clash. Its solver can only
answer "can these rules hold together?", one solve per question. Write
`deletion_filter(rules, feasible)` in `filters.py`:

- `rules` is a list of rule names; `feasible(subset)` returns `True` when the rules in `subset` can
  all hold together.
- Return one conflict: a list of rules that cannot hold together, from which no rule can be dropped
  without the rest becoming feasible. Keep the rules in the order they were given.
- Start with every rule kept. Then take the rules one at a time, in the order given, each exactly
  once: ask whether the rules kept so far, without this one, are still infeasible. If they are,
  drop this rule for good; if not, it stays. A rule dropped early is never asked about again, so the
  conflict whose rules come last in the list is the one that survives, and the caller decides which
  conflict is reported by ordering the rules.
- When all the rules can hold together, there is no conflict: return an empty list. One call of
  `feasible` on the whole list before the loop is allowed for this, and the worked solution makes it;
  it is not one of the per-rule tests.

The tests replace the solver with a small oracle. About eight lines.
