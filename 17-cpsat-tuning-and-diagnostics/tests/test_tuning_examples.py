"""The module 17 examples: the CP-SAT plan, hints, assumptions, reproducible runs and the log."""

from ortools.sat.python import cp_model

from cpsat_plan import build, schedule
from gridcap import generate
from log_events import events
from read_log import mask, section
from which_flags import conflict, minimal


def one_worker(**params) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    for name, value in params.items():
        setattr(solver.parameters, name, value)
    return solver


def test_the_small_plan_matches_the_mathopt_model_without_crews_and_drops_with_them():
    small = generate("small")
    without = build(small, crews=False)
    solver = one_worker()
    assert solver.solve(without.model) == cp_model.OPTIMAL
    assert solver.objective_value == 24260          # lesson 6.4.1's MathOpt optimum
    with_crews = build(small)
    solver = one_worker()
    assert solver.solve(with_crews.model) == cp_model.OPTIMAL
    assert solver.objective_value == 22741


def test_the_small_plan_keeps_its_budgets_and_must_dos():
    small = generate("small")
    plan = build(small)
    solver = one_worker()
    solver.solve(plan.model)
    starts = schedule(plan, solver)
    assert all(p.project_id in starts for p in small.projects if p.must_do)
    for y in small.years:
        assert sum(small.project(pid).spend(t).get(y, 0) for pid, t in starts.items()) <= small.budget[y]


def test_flags_off_by_default_and_one_per_rule_group():
    small = generate("small")
    assert build(small).flags == {}
    assert len(build(small, flags=True).flags) == 28


def test_the_infeasible_scenario_shrinks_to_p017_and_its_two_budget_years():
    core = conflict(list(build(generate("small"), flags=True).flags))
    assert core is not None
    assert sorted(minimal(core)) == ["budget_2030", "budget_2031", "must_P017"]


def test_a_feasible_hint_fixed_in_place_is_optimal_and_an_overspending_one_is_not():
    small = generate("small")
    plan = build(small)
    solver = one_worker()
    solver.solve(plan.model)
    starts = schedule(plan, solver)
    for scale, want in ((1.0, cp_model.OPTIMAL), (0.9, cp_model.INFEASIBLE)):
        check = build(small, budget_scale=scale)
        for (pid, t), var in check.x.items():
            check.model.add_hint(var, 1 if starts.get(pid) == t else 0)
        solver = one_worker(fix_variables_to_their_hinted_value=True)
        assert solver.solve(check.model) == want


def test_one_worker_with_a_seed_repeats_its_counts():
    small = generate("small")
    runs = []
    for _ in range(2):
        plan = build(small)
        solver = one_worker(random_seed=4)
        solver.solve(plan.model)
        runs.append((solver.objective_value, solver.num_branches, solver.num_conflicts, schedule(plan, solver)))
    assert runs[0] == runs[1]


def test_mask_hides_times_and_keeps_counts():
    assert mask("#1       0.03s best:4100 next:[4101,5200] main") == "#1       <time> best:4100 next:[4101,5200] main"
    assert mask("walltime: 0.137137") == "walltime: <time>"
    assert mask("deterministic_time: 0.0546806") == "deterministic_time: 0.0546806"


def test_section_stops_at_a_blank_line_or_the_next_header():
    log = ["a", "Initial x", "#Variables: 3", "", "b", "Presolved x", "#Variables: 2", "Preloading"]
    assert section(log, "Initial") == ["Initial x", "#Variables: 3"]
    assert section(log, "Presolved", "Preloading") == ["Presolved x", "#Variables: 2"]


def test_events_reads_kinds_values_and_workers():
    log = ["#Bound   0.01s best:-inf  next:[1827,27576] main (initial_propagation)",
           "#1       0.01s best:20625 next:[20626,27576] main", "#Done    0.14s main"]
    found = events(log)
    assert [e["kind"] for e in found] == ["bound", "solution", "done"]
    assert found[1]["best"] == "20625" and found[0]["next"] == ("1827", "27576") and found[2]["worker"] == "main"
