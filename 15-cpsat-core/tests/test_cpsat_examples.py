"""The module 15 examples: CP-SAT variables and rows, native logic, scaling, callbacks and the solver comparison."""

import itertools
import math
from fractions import Fraction

import pytest
from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import (EXACT, allowed_assignments, funded, mathopt_selection, one_worker, selection,
                          solve_highs)


@pytest.fixture(scope="module")
def small():
    return generate("small")


def solve(sel):
    solver = one_worker()
    assert solver.solve(sel.model) == cp_model.OPTIMAL
    return solver


def test_cpsat_and_highs_agree_on_the_lesson_model(small):
    solver = solve(selection(small))
    model, x, k = mathopt_selection(small)
    result = solve_highs(model, EXACT)
    assert solver.objective_value == pytest.approx(25_374)
    assert result.objective_value() == pytest.approx(25_374)


def test_native_and_linear_rules_allow_the_same_best_plan(small):
    assert solve(selection(small, native=True)).objective_value == solve(selection(small)).objective_value


def test_the_plan_keeps_every_rule(small):
    sel = selection(small)
    solver = solve(sel)
    plan = set(funded(sel, solver))
    borrowed = 500 * solver.value(sel.k)
    assert sum(small.project(i).capex for i in plan) <= small.capital_budget + borrowed
    assert all(p.project_id in plan for p in small.projects if p.must_do)
    assert all(p.parent in plan for p in small.projects if p.parent and p.project_id in plan)


@pytest.mark.parametrize("rows, names, expected", [
    (lambda m, v: m.add_bool_or(v["a"], v["b"]), "ab", ["01", "10", "11"]),
    (lambda m, v: m.add_implication(v["a"], v["b"]), "ab", ["00", "01", "11"]),
    (lambda m, v: m.add_at_most_one(v["a"], v["b"], v["c"]), "abc", ["000", "001", "010", "100"]),
    (lambda m, v: m.add_bool_or(~v["a"], ~v["b"], v["c"]), "abc", ["000", "001", "010", "011", "100", "101", "111"]),
    (lambda m, v: m.add_bool_or(v["b"], v["c"]).only_enforce_if(v["a"]), "abc",
     ["000", "001", "010", "011", "101", "110", "111"]),
])
def test_logic_constraints_allow_their_truth_tables(rows, names, expected):
    assert allowed_assignments(rows, names) == expected


def test_a_conditional_row_holds_only_when_its_literal_is_true():
    for on in (0, 1):
        model = cp_model.CpModel()
        b = model.new_bool_var("b")
        y = model.new_int_var(0, 10, "y")
        model.add(y <= 3).only_enforce_if(b)
        model.add(b == on)
        model.maximize(y)
        solver = one_worker()
        solver.solve(model)
        assert solver.value(y) == (3 if on else 10)


def test_scaling_a_row_keeps_its_plans():
    need, capacity = [Fraction(c) for c in ("1.5", "2.5", "0.75", "3.5", "2.5")], Fraction("7.6")
    m = math.lcm(*(f.denominator for f in need))
    whole, rhs = [int(f * m) for f in need], math.floor(capacity * m)
    for xs in itertools.product((0, 1), repeat=len(need)):
        assert (sum(c * x for c, x in zip(need, xs)) <= capacity) == (sum(c * x for c, x in zip(whole, xs)) <= rhs)


def test_enumeration_at_the_optimum_finds_every_tied_plan():
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"x{i}") for i in range(4)]
    model.add(sum(x) <= 2)
    model.add(sum(x) == 2)                 # value 1 each: every pair of two is optimal

    class Collect(cp_model.CpSolverSolutionCallback):
        def __init__(self):
            super().__init__()
            self.plans = set()

        def on_solution_callback(self):
            self.plans.add(tuple(self.value(v) for v in x))

    collect = Collect()
    solver = one_worker()
    solver.parameters.enumerate_all_solutions = True
    assert solver.solve(model, collect) == cp_model.OPTIMAL
    assert len(collect.plans) == 6


def test_cpsat_proves_the_small_sequencing_optimum():
    from sequencing import circuits, with_cpsat, with_highs
    jobs = circuits(8)
    assert with_cpsat(jobs)[:2] == ("OPTIMAL", 100)
    assert with_highs(jobs)[0] == "OPTIMAL"
