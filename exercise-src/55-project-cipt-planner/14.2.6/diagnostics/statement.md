Two messages arrived the same week. From finance, after trying a budget cut:

> We cut 2030 and 2031 to $4M each and the planner just said "infeasible". Infeasible why? Which of
> our numbers is the problem?

And from a regional manager:

> P030 is our biggest Valley project and it's not funded. Why not? What would it take?

You start from the planner of the lesson before, whose rows all carry names. When a request has no
plan, name exactly the rules that clash, in the planners' words, so that dropping or changing any
one of them gives a plan; a rule that plays no part in the clash is not named. When a project is
left out, say what funding it would cost (the NPV given up and the projects dropped) or, when no
plan can fund it, which rules block it. The command line explains an infeasible request, and
`--why PROJECT` explains a project the plan leaves out.

`--why` for a project the plan funds prints nothing after the report; for an infeasible request
the command line prints the conflict, does not answer `--why`, and returns 1.

Run's report gains a section: `main.py` now asks why P003 was left out of the demo plan, as
`--why P003` does. After the report it prints `P003 cannot be funded. ` and the conflict message on
the same line; the message's first line is
`No plan meets these <n> rules together; drop or change any one of them:` and each next line is
`  <row>: <description>` (two spaces first), one per row of the conflict in name order. The
frontier section of the lesson before follows, unchanged.

`cipt/scenario.py` and `cipt/store.py` are the next lesson's stubs, as the reference has them; no
code of this step imports them, so leave them as they are. Submit runs every test in `tests/`, the
earlier steps' included, and compares Run's report with the expected one.
