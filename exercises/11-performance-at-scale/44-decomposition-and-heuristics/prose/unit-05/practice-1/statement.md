A water utility rolls its pipe-renewal plan forward year by year. Its planners use a variant of the
lesson's rolling horizon called **relax-and-fix**: in each window, the starts in the window's years
are yes/no, and the starts in every *later* year are kept in the model as continuous variables
between 0 and 1, instead of being held at 0. The later years are then a cheap look ahead: the
window sees roughly what its choices leave for later. As before, the first `keep` years of each
window are kept, starts decided in earlier windows are fixed, and the last window keeps everything.

The years are the calendar years of `budgets`, in order, and every start year a project offers is
one of them. A window is `window` consecutive years of that list, and its decisions are the starts
*in* those years: a start is yes/no when its year is in the window or earlier, and relaxed when it
is later. The first window begins at the first year, and each next one begins `keep` years later.
The last window is the first one that reaches the final year of `budgets` (or would run past it, in
which case it is cut short at that year); it keeps every start it has not yet fixed, and the plan
ends there. With 2027 to 2029, `window=2` and `keep=1`, the first window 2027-2028 keeps 2027, and
the second, 2028-2029, is the last and keeps 2028 and 2029.

`build(projects, budgets)` gives the whole plan model (at most one start per project, a budget row
per year counting each project's spend in every year of work). Write first which variables a window
fixes, which it makes integer and which continuous, and what it keeps. Then write
`relax_and_fix(projects, budgets, window, keep)` and return the plan, a dict from project name to
start year. `projects[n]` holds `"value"` (start year to value) and `"cost"` (spend by year of work).
A MathOpt variable becomes continuous with `var.integer = False`.

About fifteen lines.
