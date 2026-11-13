A gas utility plans its pipe replacements by quarter, and its planning tool keeps each scenario as a
record: a name and a plan, the list of funded replacements, each with an `id` and a `start` such as
`"2028-Q3"`. Every time a scenario is re-run, the program managers ask the same thing: what changed
since the last one? Write the function the tool will call for it, `diff_scenarios(a, b)` in
`gas_plan.py`, comparing scenario `a`'s plan with scenario `b`'s. It returns a dictionary:

- `"adds"`: the ids in `b`'s plan and not in `a`'s, sorted;
- `"drops"`: the ids in `a`'s plan and not in `b`'s, sorted;
- `"shifts"`: one entry per id in both plans with a different start, sorted by id, each a dictionary
  `{"id", "from", "to", "quarters"}` where `quarters` is how many quarters later `b` starts it than
  `a` does (negative when earlier).

Plans list their rows in any order. Write `quarters(start)` first, a count of quarters that makes
the difference of two starts the number of quarters between them, and say how $`(y, q)`$ maps to
one integer. Then state the three lists as set expressions over $`P_a`$ and $`P_b`$, the ids of the
two plans, and $`a(i)`$, $`b(i)`$, their starts. The tests use their own pipes.
