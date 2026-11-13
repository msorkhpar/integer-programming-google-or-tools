The asset team sent the first request:

> **Request 1.** We have $10,000k for transformer replacements in 2027. Replace the worst
> transformers we can afford. The list must be repeatable, so put it in code, with tests.

You start from the skeleton: it generates a fleet and ranks it worst condition first, stopping at the
first unit that does not fit. Keep the ranking as a baseline, and make `plan` choose with a model
instead. Each transformer is replaced this year or not, the replaced units together cost no more
than the budget, and the plan removes the most risk, where a unit's risk is its probability of
failure this year times its consequence of failure (`fleet.risk`). Build the model with MathOpt and
solve it with HiGHS. Then write `feasible`, which pins one whole list and asks the solver whether the
model allows it, so a test can show a list at the budget allowed and one just over it refused.

The starting code is the skeleton, plus the files this step adds as the reference has them, with
the blueprint's methods stubbed. `renewal/model.py` has its imports and `Built`, and the `build`
stub. `renewal/solve.py` is whole: the lesson's `FOUND`, `solve_quietly`, `is_feasible` and
`read_plan`, ready for `plan.py` to call. `renewal/risk.py` is the next step's stub; nothing in
this step imports it, so leave it as it is.

Run executes `main.py`, which plans a tiny fleet: 25 transformers of GridCap, a fictional utility,
drawn by `renewal/fleet.py` from seed 56, with a $2,000k budget, by the ranking and by the model,
and prints what each list costs and removes; `expected/report.txt` is the report it should print.
Its three lines are, with money in $k, a comma between thousands and no decimals:

```text
fleet: 25 fictional transformers, seed 56; budget $2,000k in 2027
worst first: <units> units, $<cost>k, risk removed $<risk>k
model      : <units> units, $<cost>k, risk removed $<risk>k (<status>)
```

where `<cost>` is what the list's units cost, `<risk>` the sum of `fleet.risk` over them, and
`<status>` the `Plan`'s status, the termination reason's name. Submit runs every test in `tests/`,
the skeleton's own included, and compares Run's report with the expected one.
