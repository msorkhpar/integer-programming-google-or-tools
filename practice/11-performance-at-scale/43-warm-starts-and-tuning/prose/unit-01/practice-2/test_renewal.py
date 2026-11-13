from ortools.math_opt.python import mathopt

from renewal import Job, as_hint, greedy_plan

YEARS = (2028, 2029, 2030)


def model_of(jobs, budget):
    model = mathopt.Model()
    x = {(j.name, y): model.add_binary_variable(name=f"x_{j.name}_{y}") for j in jobs for y in j.years}
    for j in jobs:
        done = sum(x[j.name, y] for y in j.years)
        model.add_linear_constraint(done == 1 if j.must else done <= 1)
    for y, b in budget.items():
        terms = [j.cost * x[j.name, y] for j in jobs if y in j.years]
        if terms:
            model.add_linear_constraint(sum(terms) <= b)
    model.maximize(sum(j.value * x[j.name, y] for j in jobs for y in j.years))
    return model, x


def spend(jobs, plan):
    out = {}
    for j in jobs:
        if j.name in plan:
            out[plan[j.name]] = out.get(plan[j.name], 0) + j.cost
    return out


JOBS = [Job("oak", 400, 600, YEARS), Job("pine", 300, 900, YEARS), Job("ash", 200, 500, (2028, 2029)),
        Job("elm", 500, 400, (2029,), must=True), Job("fir", 100, 90, YEARS)]
BUDGET = {2028: 500, 2029: 1000, 2030: 300}


def test_the_plan_keeps_every_budget_and_funds_every_must_do():
    plan = greedy_plan(JOBS, BUDGET)
    assert plan.get("elm") == 2029
    assert len(plan) >= 3
    assert all(amount <= BUDGET[y] for y, amount in spend(JOBS, plan).items())


def test_highs_accepts_the_plan_as_a_feasible_start():
    model, x = model_of(JOBS, BUDGET)
    log = []
    plan = greedy_plan(JOBS, BUDGET)
    value = sum(j.value for j in JOBS if j.name in plan)
    mathopt.solve(model, mathopt.SolverType.HIGHS,
                  model_params=mathopt.ModelSolveParameters(solution_hints=[as_hint(x, plan)]),
                  msg_cb=mathopt.list_message_callback(log))
    assert value > 0
    assert any(f"MIP start solution is feasible, objective value is {value}" in line for line in log)


def test_jobs_are_taken_by_value_per_dollar_not_by_value():
    jobs = [Job("big", 400, 800, (2028,)), Job("small-a", 200, 500, (2028,)), Job("small-b", 200, 450, (2028,))]
    assert greedy_plan(jobs, {2028: 400}) == {"small-a": 2028, "small-b": 2028}


def test_a_job_moves_to_its_next_year_when_the_earliest_is_full():
    jobs = [Job("first", 300, 900, (2028,)), Job("second", 300, 800, (2028, 2029))]
    assert greedy_plan(jobs, {2028: 400, 2029: 400}) == {"first": 2028, "second": 2029}


def test_must_do_jobs_are_placed_before_better_optional_ones():
    jobs = [Job("gem", 300, 3000, (2028,)), Job("law", 300, 300, (2028,), must=True)]
    assert greedy_plan(jobs, {2028: 400}) == {"law": 2028}


def test_a_job_that_fits_nowhere_does_not_stop_the_fill():
    jobs = [Job("huge", 900, 2700, (2028,)), Job("tiny", 100, 200, (2028,))]
    assert greedy_plan(jobs, {2028: 300}) == {"tiny": 2028}


def test_the_start_gives_every_variable_a_value():
    model, x = model_of(JOBS, BUDGET)
    hint = as_hint(x, greedy_plan(JOBS, BUDGET))
    assert set(hint.variable_values) == set(x.values())


def test_must_do_jobs_compete_by_value_per_dollar_among_themselves():
    jobs = [Job("law-a", 300, 300, (2028,), must=True), Job("law-b", 300, 600, (2028,), must=True)]
    assert greedy_plan(jobs, {2028: 400}) == {"law-b": 2028}
