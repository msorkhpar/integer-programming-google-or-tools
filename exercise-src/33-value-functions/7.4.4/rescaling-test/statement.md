A transit agency's analysts keep rewriting the function that values its projects. Before any new
version is used, the agency wants an automatic check that the version does not care what units the
data arrived in: if every measure and its reference are restated in other units (hours to minutes,
dollars to thousands of dollars), the projects must come out in the same order.

Write two functions in `rescaling.py`:

- `ranking(values)`: the project names from the highest value to the lowest. Values closer than
  `TIED` count as equal, and equal values are listed in name order. Near-ties **chain**: walk down
  the names sorted by value, and put each one in the same tied group as the name just before it when
  the two values are within `TIED`. So three values each within `TIED` of the next form one group,
  listed in name order, even if the first and the last are further apart. Floating-point arithmetic
  rounds: two values that are equal on paper can differ in their last digit, and in the other
  direction once the units change. Rounding alone must never make the check fail.
- `survives_rescaling(value, benefits, reference, factors)`: `value(benefit, reference)` is the
  function under test, `benefits[project]` maps each measure to an amount, and `factors[measure]` is
  how many new units one old unit is. Restate every amount and every reference, rank the projects
  before and after, and return whether the two rankings are the same.

The tests pass in a normalized value function, which must pass the check, and a raw sum, which must
fail it. About fifteen lines.
