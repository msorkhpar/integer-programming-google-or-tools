A utility's training week (not GridCap) has more proposed talks than it can run. Each talk has a
speaker, a value, and a number of hours of the one shared demonstration lab, which is open for
$`H`$ hours over the week. Two rules: a speaker gives at most one talk, and the lab hours of
**any two** accepted talks must fit together within $`H`$ (the lab is booked in pairs of sessions;
that is the planners' rule, take it as given). With $`x_t \in \{0, 1\}`$ for "talk $`t`$ is
accepted", the model maximizes $`\sum_t v_t\, x_t`$.

Write two functions in `programme.py`:

- `clashes(talks, lab_hours)`: the pairs of talks that no allowed programme accepts together, as a
  set of `frozenset({name, name})`;
- `add_clash_rows(model, x, pairs)`: rows that refuse exactly those pairs, written so the LP bound
  is as tight as you can make it, and returning how many rows were added.

Pair rows $`x_a + x_b \le 1`$ would refuse the right programmes, but the lesson showed why they leave
the LP loose. Decide on paper which groups of talks can share one "at most one" row, why that row is
valid, and how to cover every clash with such rows. Then write the rows with labels before coding.

The tests try every programme of five talks against the rules, so any correct set of rows passes
them; two of them also check the LP bound. About twenty lines.
