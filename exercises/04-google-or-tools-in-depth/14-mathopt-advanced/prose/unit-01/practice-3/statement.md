A scheduling team's service accepts models from several modelers and must solve each with the
first solver, in a preferred order, that accepts it. When a solver refuses a model, the team wants
the refusal's real reason in its log, in the solver's own words.

Write `solve_first(model, solvers)`. It tries `mathopt.solve(model, s)` for each solver type `s` in
`solvers`, in order, and returns a tuple `(solver, result, reasons)`:

- `solver` and `result`: the first solver that solved the model without raising, and its
  `SolveResult`; both `None` if every solver raised;
- `reasons`: a dict from each refusing solver's name (`s.name`, such as `"HIGHS"`) to the reason it
  gave, as a string. Solvers after the one that succeeded are not tried and not listed.

In OR-Tools 9.15 a refusal arrives as an `AttributeError` about `canonical_code`; the solver's own
message is the exception's `__context__` (lesson 4.3.1). Record that message, and fall back to the
exception itself if `__context__` is empty. Either form of the message passes: the hidden error's
text, `str(error.__context__)`, which is the message with the status code's name in brackets (what
the lesson's `refusal` returns), or its `.message` alone (what lesson 4.2.4 reads). The tests check
only that the reason contains the solver's own words, such as "does not support indicator
constraints". About ten lines.
