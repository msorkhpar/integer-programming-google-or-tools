The rate-case settlement for the Plains region sent the second request:

> **Request 2.** Plains should get its fair share of the work: at least a quarter of the capital
> spend, every year. The settlement is signed; the plan for the next cycle must keep it.

The planners answered the two open questions: the share is of what the plan spends, not of the
budget, and it holds in every plan year. The change is proposed and archived in `openspec/`: its
proposal, its delta with the regional share and the checks of shares, its design and its tasks, and
the living capital-plan spec now states both requirements. The specs, the tests (one per scenario,
named after it) and the expected report are given and read-only.

You start from the planner of the last lesson, where `Request.shares` is a stub the model ignores.
Make the plan give each named region at least its share, in whole percent, of what the plan spends in
every plan year, with integer coefficients, since CP-SAT takes integers only. Refuse, before solving,
shares that no plan with any spend could keep. Count each region's share in the report apart from
the model.

Run executes `main.py`, which plans a tiny portfolio: 12 projects of GridCap, a fictional utility,
drawn by `capplan/portfolio.py` from seed 58, over three years with $1,500k a year and a 25% share for
Plains, and prints each year's starts, spend and Plains share, then the line about the specs;
`expected/report.txt` is the report it should print. Submit runs every test in `tests/`, the earlier
steps' included, and compares Run's report with the expected one.
