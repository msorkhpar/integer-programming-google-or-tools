"""The module 43 examples: rolling a plan forward, starts, the run records, and the measures built on them."""

import math

import pytest
from ortools.math_opt.python import mathopt

from cycles import next_cycle
from gridcap import generate
from plan_model import PORTFOLIO_SEEDS, REGIONS, broken, build, instance_set, keys, value
from runs import Run, highs, hint_values, progress_rows
from sgm import compare, shifted_geometric_mean
from start_bench import best_by
from starts import carry_forward, greedy_fill, greedy_plan, repair


@pytest.fixture(scope="module")
def ridge():
    return instance_set()[0]


@pytest.fixture(scope="module")
def rolled(ridge):
    approved = highs(ridge, 1).plan
    nxt, committed = next_cycle(ridge, approved, seed=7)
    return approved, nxt, committed


def test_the_instance_set_is_eight_regions_with_every_parent_before_its_children():
    plans = instance_set()
    assert [pf.name for pf in plans] == [f"{r}-{s}" for s in PORTFOLIO_SEEDS for r in REGIONS]
    for seed in PORTFOLIO_SEEDS:
        order = {p.project_id: n for n, p in enumerate(generate("medium", seed).projects)}
        assert all(order[p.parent] < order[p.project_id] for p in generate("medium", seed).projects if p.parent)


def test_every_must_do_fits_its_regions_budget_at_its_earliest_start():
    for pf in instance_set():
        plan = {p.project_id: p.earliest_start for p in pf.projects if p.must_do}
        assert not [r for r in broken(pf, plan) if r.startswith("budget_")]


def test_the_solved_plan_breaks_no_row_and_is_worth_the_objective(ridge):
    run = highs(ridge, 1)
    assert run.status == "optimal"
    assert broken(ridge, run.plan) == []
    assert value(ridge, run.plan) == pytest.approx(run.objective)


def test_broken_agrees_with_the_model_on_a_plan_that_breaks_rows(rolled):
    approved, nxt, _ = rolled
    carried, _ = carry_forward(approved, nxt)
    assert broken(nxt, carried)
    pm = build(nxt)
    for (i, t), v in pm.x.items():
        fixed = 1.0 if carried.get(i) == t else 0.0
        v.lower_bound = v.upper_bound = fixed
    result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.INFEASIBLE


def test_next_cycle_commits_the_first_year_and_takes_its_spend_off_the_budgets(ridge, rolled):
    approved, nxt, committed = rolled
    assert committed == {i for i, t in approved.items() if t == ridge.years[0]}
    assert nxt.years == ridge.years[1:] + (ridge.years[-1] + 1,)
    assert not committed & {p.project_id for p in nxt.projects}
    assert all(min(p.starts()) >= nxt.years[0] for p in nxt.projects)


def test_next_cycle_is_the_same_for_the_same_seed(ridge, rolled):
    approved, nxt, _ = rolled
    again, _ = next_cycle(ridge, approved, seed=7)
    assert again.content_hash() == nxt.content_hash()


def test_repaired_filled_and_greedy_starts_are_plans(rolled):
    approved, nxt, _ = rolled
    carried, report = carry_forward(approved, nxt)
    assert set(report["no variable"]) == set(approved) - set(carried)
    fixed = repair(nxt, carried)
    assert broken(nxt, fixed) == [] and set(fixed) <= set(carried)
    assert broken(nxt, greedy_fill(nxt, fixed)) == []
    assert broken(nxt, greedy_plan(nxt)) == []


def test_a_complete_start_values_every_variable(rolled):
    _, nxt, _ = rolled
    start = hint_values(keys(nxt), greedy_plan(nxt))
    assert set(start) == set(keys(nxt)) and set(start.values()) <= {0.0, 1.0}


def test_a_feasible_start_is_the_first_highs_incumbent_at_no_work(rolled):
    _, nxt, _ = rolled
    plan = greedy_plan(nxt)
    run = highs(nxt, 1, hint_values(keys(nxt), plan))
    assert run.events[0] == (0.0, value(nxt, plan))
    assert any("MIP start solution is feasible" in line for line in run.log)


def test_progress_rows_read_best_plan_and_lp_iterations():
    log = ["Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
           " J       0       0         0   0.00%   inf             4885               Large        0      0      0         0     0.0s",
           "         0       0         0   0.00%   40615.939915    37809              7.42%        0      0      4        41     0.0s",
           "Model after restart has 44 rows, 117 cols (117 bin., 0 int., 0 impl., 0 cont., 0 dom.fix.), and 276 nonzeros",
           "Solving report"]
    assert progress_rows(log) == [("J", 4885.0, 0.0), ("", 37809.0, 41.0)]


def test_run_measures():
    run = Run("X", "i", 1, "optimal", 100.0, 100.0, 50.0, ((0.0, 80.0), (10.0, 99.5), (40.0, 100.0)))
    assert run.first() == 0.0
    assert run.within(100.0, 0.01) == 10.0
    assert run.within(100.0, 0.0) == 40.0
    assert Run("X", "i", 1, "x", 0, 0, 0).within(1.0, 0.1) == math.inf
    assert best_by(run, 5.0) == 80.0 and best_by(run, -1.0) == -math.inf


def test_compare_is_a_ratio_of_shifted_geometric_means_with_wins_and_losses():
    assert shifted_geometric_mean([0.0, 0.0], 10) == pytest.approx(0.0)
    ratio, wins, losses = compare([100.0, 300.0, 50.0], [200.0, 300.0, 40.0], shift=10)
    assert (wins, losses) == (1, 1)
    assert ratio == pytest.approx(shifted_geometric_mean([100.0, 300.0, 50.0], 10)
                                  / shifted_geometric_mean([200.0, 300.0, 40.0], 10))
