A water utility decides which pumping stations to commission this year (yes or no each) and how
many hours of contractor overtime to buy, any amount up to a cap. A limit row, such as the
capital budget, caps what stations and overtime use together. After the MILP is solved, finance
reads the fixed-integer price of that row and asks two questions: if the limit rises by `step`,
does the plan (stations held as chosen) gain exactly price × `step`? And if it falls by `step`,
does it lose exactly price × `step`?

Write `price_directions(model, result, row_name, step)` for a solved MILP whose `row_name` row is
a $`\le`$ row. It returns a dict:

- `"price"`: the row's dual value in the fixed-integer LP;
- `"up"`: `True` when the fixed-integer LP with the row's limit raised by `step` is optimal and
  its value is the original fixed LP's value plus price × `step` (within `1e-6`);
- `"down"`: the same for the limit lowered by `step`, with value minus price × `step`.

`fix_plan(model, result)` is given: it fixes every integer variable at its value in `result` and
makes it continuous. It changes the caller's model in place, and your function may leave the plan
fixed there: afterwards the tests read only the row's limit. Find the row by
its name as the lesson's `selection.row` does (MathOpt has no lookup by name). Solve each LP with
GLOP. Put the row's limit back where it was before you return.

State first, with the plan fixed, which values of `step` you expect to hold upward and downward,
in terms of the continuous variable's value and its bounds. The tests build small station models
and check your answers. About twelve lines.
