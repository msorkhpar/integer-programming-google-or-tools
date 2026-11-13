The water utility of the previous practice now improves its plan with LNS. One step takes the
current plan and a neighborhood, a set of project names, and re-plans the neighborhood while every
other project stays as the plan has it.

`build(projects, budgets)` gives the whole plan model. Write first the step's model: which start
variables it fixes, to which values, and which it leaves free. Then write
`lns_step(projects, budgets, plan, free)` to solve it with HiGHS through MathOpt and return the
better of the re-planned plan and `plan` (a dict from project name to start year). The tests use
small plans whose best answers are known.

About eight lines.
