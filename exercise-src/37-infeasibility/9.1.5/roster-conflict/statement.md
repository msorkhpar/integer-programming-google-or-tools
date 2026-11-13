A hospital ward builds its weekly nurse roster with CP-SAT. Three kinds of rules apply:

| Rule name | Rule |
| --- | --- |
| `cover_<day>` | at least `need[day]` nurses work on that day |
| `max_<nurse>` | the nurse works at most `max_shifts[nurse]` days in the week |
| `off_<nurse>_<day>` | the nurse does not work on that day (a granted request) |

When no roster exists, the ward manager wants the rules that clash, by name. Write the formulation
first: a 0/1 variable per nurse and day, and each rule as one constraint guarded by its own Boolean
flag. Then write `named_conflict(nurses, need, max_shifts, days_off)`:

- build the model, assume every flag, and solve with one worker;
- if a roster exists, return `None`;
- otherwise return the sorted names of the rules whose flags the solver reports in
  `sufficient_assumptions_for_infeasibility()`.

`nurses` is a list of names (no underscores), `need` maps each day of the week (an integer) to the
nurses needed, `max_shifts` maps each nurse to a limit, and `days_off` is a list of
`(nurse, day)` pairs. A day off on a day that is not a key of `need` forbids nothing: it gets no
rule and no name. CP-SAT here only decides whether a roster exists, so there is no objective and
no gap tolerance to set. The set the solver reports is sufficient, not always minimal, so the tests
check that the names you return are infeasible together and include the rules that must be there.
About twenty lines.
