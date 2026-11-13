This is the mock's whiteboard, coded. A gas utility's leak repairs each have a `cost`, an `npv` and
the safety `risk` they remove, all in $k. Repairs that name the same `main` are alternatives for that
main; a repair with `main=None` belongs to no group. The planners' question: **the most NPV within
the budget, among the plans that remove at least `risk_floor` of risk**, with at most one repair per
main.

`repairs.py` already creates one binary per repair. Write `add_epsilon_model(model, x, repairs,
budget, risk_floor)`: the objective and every row. Write the formulation first (sets, parameters,
variables with domains, objective with its sense, labelled rows), then code it.

The tests fix plans in and out and ask HiGHS whether the model accepts them, then solve the model
and check the best plan, so any correct formulation passes. About ten lines.
