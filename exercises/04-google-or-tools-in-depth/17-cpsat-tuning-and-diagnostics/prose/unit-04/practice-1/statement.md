A warehouse team keeps its CP-SAT logs and wants a dashboard of how much presolve shrinks each
model. A CP-SAT log describes the model twice: in the block that starts with `Initial optimization
model` (the model as written) and in the block that starts with `Presolved optimization model`
(the model after presolve). In each, the line starting `#Variables:` gives the number of variables.

Write `variables_before_and_after(log)` in `log_sizes.py`. `log` is the whole log as one string.
Return a pair of integers: the variable count before presolve and after it.

Write the helper `variables_in(log, header)` first: find the line that starts with `header`, then
the first `#Variables:` line after it. CP-SAT writes large counts with an apostrophe between
thousands, as in `#Variables: 1'331`. About eight lines.
