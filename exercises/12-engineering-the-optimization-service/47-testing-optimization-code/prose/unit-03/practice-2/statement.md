The line-maintenance group's golden test (practice 1) now says *what* changed, but a reviewer still
has to decide *what kind* of change it is before deciding what to do. Write the triage.

The docstring of `triage.py` gives a record's shape. The roster model **minimizes** cost. Write
`classify(expected, actual)`, returning one word:

- `"input"` when the two records were solved from different data (their `input` hashes differ);
  nothing else about them can be compared, so this answer wins over every other;
- `"status"` when the solver's status differs;
- `"better"` or `"worse"` when the costs differ by more than `COST_TOLERANCE` dollars, by which way
  the cost moved;
- `"tie"` when the costs are the same within the tolerance but the assignments differ: another
  roster of equal cost;
- `"same"` when nothing differs beyond the tolerance.

About eight lines.
