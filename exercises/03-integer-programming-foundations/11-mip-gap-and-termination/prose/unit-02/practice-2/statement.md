A school-bus routing team replays old solver runs to choose stopping rules for next term. For each
past run they kept a **trace**: the solver's progress at a few moments, oldest first. Each row is a
dict with these keys:

- `"seconds"`: wall-clock time since the start;
- `"nodes"`: branch-and-bound nodes done;
- `"solutions"`: plans found so far;
- `"incumbent"`: the best plan's objective value, or `None` before the first plan;
- `"bound"`: the best bound.

The model is a maximization, and every incumbent in a trace is positive.

Write `where_it_stops(trace, limits)` in `first_limit.py`. `limits` holds some of the keys
`"relative_gap"`, `"absolute_gap"`, `"nodes"`, `"solutions"` and `"seconds"`. Return
`(index, rule)`: the index of the first row at which a rule in `limits` is met, and that rule's key.
If no rule is met on any row, return `(None, None)`.

A rule is met on a row when:

- `"relative_gap"`: the row has an incumbent and $`(\text{bound} - \text{incumbent}) / \text{incumbent}`$
  is at most the limit;
- `"absolute_gap"`: the row has an incumbent and $`\text{bound} - \text{incumbent}`$ is at most the
  limit;
- `"nodes"`, `"solutions"`, `"seconds"`: the row's value is at least the limit.

A row with no incumbent meets no gap rule. When several rules are met on the same row, name the first
in this order: `"relative_gap"`, `"absolute_gap"`, `"nodes"`, `"solutions"`, `"seconds"`. A gap rule
comes first because a solver that meets one reports the run as optimal.
