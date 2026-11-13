A water utility's capital plan chooses which mains to work on. Some mains have two options, reline
or replace, in an alternative group: at most one option per main. For every project the plan
defers, the utility's analyst has already forced it in and re-solved, so for each one there is the
best plan and the forced plan. The asset managers want the reason written from those two plans,
in the terms they use: which alternative the deferred option would push out, and which other
projects would give way.

In `reasons.py`, write `why_deferred(name, group_of, best, forced)`:

- `group_of` maps a project to its alternative group; a project with no group is absent;
- `best` is the set of projects in the best plan, and `forced` the set with `name` forced in, or
  `None` when no plan allows it.

Return a list of strings:

- `["infeasible"]` when there is no forced plan;
- `["nothing displaced"]` when the forced plan drops nothing from the best one;
- otherwise one entry per project the forced plan drops: `"alternative <id>"` when it is in the same
  alternative group as `name`, `"displaced <id>"` when it is not. Alternatives come first, then the
  rest, each part sorted by id.

The forced plan was solved with $`\sum_{t} x_{\text{name},t} = 1`$ added, and each group $`g`$ keeps
$`\sum_{i \in g} \text{started}(i) \le 1`$. Before coding, say which of those rows makes a dropped
project an "alternative", and what a project with no group can never have. The tests use their own
mains.
