A utility's line-maintenance group assigns jobs to crews with a model that minimizes cost, and keeps
golden records of a few rosters. Their regression test compares records with `==` and fails with a
screen of nested dictionaries whenever anything moves, including the last digits of a float. Write
the comparison that replaces it.

The docstring of `roster_golden.py` gives a record's shape, and `TOLERANCE` gives what "the same"
means for each float field, in that field's own units: $1 for cost, 0.01 hours for overtime.
Write `compare(expected, actual)`, returning one line per difference, in this order and format:

- if the status differs, only `status: <old> -> <new>`, and nothing else, because a roster that did
  not solve cannot be compared field by field;
- `cost: <old> -> <new>`, both with two decimals, if the costs differ by more than the tolerance;
- for each job in either record, in sorted order, `assign: <job> <old crew> -> <new crew>` if its
  crew differs, writing `none` for a record that does not assign it;
- for each crew in either record, in sorted order, `overtime <crew>: <old> -> <new>`, two decimals,
  if the hours differ by more than the tolerance; a crew a record does not list has 0 hours.

An identical record gives an empty list. About fifteen lines.
