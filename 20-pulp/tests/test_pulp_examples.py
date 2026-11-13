"""The module 20 examples: the PuLP port of lesson 6.4.1's model, the inherited script, its traps, its port."""

import json
import subprocess
import sys
import warnings
from dataclasses import replace
from pathlib import Path

import pulp
import pytest
from ortools.math_opt.python import mathopt

import mathopt_selection
import pulp_timing
from gridcap import generate
from legacy_selection import solve_legacy
from plan_rules import broken_rules

ROOT = Path(__file__).resolve().parents[2]
# PuLP 3.3 warns that PULP_CBC_CMD and LpVariable(...) go away in 4.0; the lessons say so, the runs stay quiet.
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

# MathOpt's HiGHS crashes on a MIP in a process that has imported pulp (highs_after_pulp.py), and this
# one has. So the HiGHS side runs module 26's own builder, the one lesson 6.4.1 solved, in a child process.
HIGHS_CHILD = """
import json, sys
from ortools.math_opt.python import mathopt
from gridcap import generate
from timing_model import build, schedule
tm = build(generate(sys.argv[1]))
result = mathopt.solve(tm.model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
print(json.dumps({"reason": result.termination.reason.name, "value": result.objective_value(),
                  "plan": schedule(tm, result), "rows": sorted(c.name for c in tm.model.linear_constraints())}))
"""


def highs_in_child(size: str) -> dict:
    env_path = f"{ROOT / '00-base'}:{ROOT / '26-multi-period-timing' / 'src'}"
    done = subprocess.run([sys.executable, "-c", HIGHS_CHILD, size], capture_output=True, text=True,
                          env={"PYTHONPATH": env_path, "PATH": "/usr/bin:/bin"}, check=True)
    return json.loads(done.stdout.strip().splitlines()[-1])


def cbc_solve(portfolio, **options):
    pt = pulp_timing.build(portfolio)
    status = pt.prob.solve(pulp_timing.cbc(**options))
    return pt, status


@pytest.mark.parametrize("size", ["tiny", "small"])
def test_pulp_with_cbc_reaches_the_optimum_mathopt_with_highs_found_in_lesson_6_4_1(size):
    portfolio = generate(size)
    pt, status = cbc_solve(portfolio, gapRel=0)
    highs = highs_in_child(size)
    assert status == pulp.LpStatusOptimal and pt.prob.sol_status == pulp.LpSolutionOptimal
    assert highs["reason"] == "OPTIMAL"
    assert pulp.value(pt.prob.objective) == pytest.approx(highs["value"])
    cbc_plan = pulp_timing.schedule(pt)
    assert broken_rules(portfolio, cbc_plan) == []
    assert broken_rules(portfolio, {pid: int(t) for pid, t in highs["plan"].items()}) == []
    assert sorted(row.name for row in pt.prob.constraints()) == highs["rows"]


def test_small_reaches_the_value_lesson_6_4_1_printed():
    pt, _ = cbc_solve(generate("small"), gapRel=0)
    assert pulp.value(pt.prob.objective) == pytest.approx(24_260)


def test_the_module_mathopt_copy_builds_the_same_rows_as_module_26():
    from mathopt_timing import build
    model, x = build(generate("small"))
    assert sorted(c.name for c in model.linear_constraints()) == highs_in_child("small")["rows"]
    assert len(x) == 80


def test_one_node_reports_optimal_status_with_an_unproved_solution():
    pt, status = cbc_solve(generate("small"), maxNodes=1)
    assert status == pulp.LpStatusOptimal
    assert pt.prob.sol_status == pulp.LpSolutionIntegerFeasible
    assert pulp.value(pt.prob.objective) < 24_260


def test_iadd_of_true_adds_no_row_and_of_false_raises():
    prob = pulp.LpProblem("t", pulp.LpMaximize)
    x = pulp.LpVariable("x", 0, 1)
    prob += x, "obj"
    prob += (1.0 == 1), "lock"
    assert prob.numConstraints() == 0
    with pytest.raises(TypeError):
        prob += (1.0 == 0), "lock"


def test_a_chained_comparison_keeps_only_its_right_side():
    x = pulp.LpVariable("x", 0, 10)
    row = 2 <= x <= 5
    assert row.sense == pulp.LpConstraintLE and -row.constant == 5


def test_a_bare_expression_replaces_the_objective_with_a_warning():
    prob = pulp.LpProblem("t", pulp.LpMaximize)
    x = pulp.LpVariable("x", 0, 10)
    prob += 3 * x, "value"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        prob += x + 1
    assert str(prob.objective) == "x + 1"
    assert any("Overwriting" in str(w.message) for w in caught)


def test_names_collide_after_pulp_rewrites_them():
    prob = pulp.LpProblem("t", pulp.LpMaximize)
    x = pulp.LpVariable("x", 0, 10)
    prob += x <= 1, "budget-2027"
    with pytest.raises(pulp.PulpError):
        prob += x <= 2, "budget_2027"
    y = pulp.LpVariable.dicts("y", ["P-017", "P_017"], cat="Binary")
    twice = pulp.LpProblem("twice", pulp.LpMaximize)
    twice += y["P-017"] + y["P_017"], "v"
    with pytest.raises(pulp.PulpError):
        twice.checkDuplicateVars()


def test_an_infeasible_solve_returns_a_truthy_code_and_leaves_values_behind():
    small = generate("small")
    tight = replace(small, capital_budget=sum(p.capex for p in small.projects if p.must_do) - 1000)
    status, total, funded, prob = solve_legacy(tight)
    assert status == "Infeasible" and prob.status == pulp.LpStatusInfeasible and bool(prob.status)
    assert total is not None and funded
    reason, value, plan, _ = mathopt_selection.solve_ported(tight, mathopt.SolverType.GSCIP)
    assert reason == "INFEASIBLE" and value is None and plan == []


def test_a_variable_outside_the_problem_has_no_value():
    x = pulp.LpVariable.dicts("x", ["a", "b"], cat="Binary")
    prob = pulp.LpProblem("t", pulp.LpMaximize)
    prob += x["a"], "v"
    prob += x["a"] <= 1, "c"
    prob.solve(pulp_timing.cbc())
    assert x["a"].varValue == 1 and x["b"].varValue is None


@pytest.mark.parametrize("size", ["tiny", "small", "medium"])
def test_the_mathopt_port_reaches_the_legacy_value_plan_and_rows_at_zero_gap(size):
    portfolio = generate(size)
    status, old_value, old_plan, prob = solve_legacy(portfolio, gap=0)
    reason, new_value, new_plan, model = mathopt_selection.solve_ported(portfolio, mathopt.SolverType.GSCIP, 0.0)
    assert (status, reason) == ("Optimal", "OPTIMAL")
    assert new_value == pytest.approx(old_value)
    assert sorted(old_plan) == sorted(new_plan)
    assert sorted(r.name for r in prob.constraints()) == sorted(c.name for c in model.linear_constraints())


def test_mathopt_highs_after_import_pulp_is_killed():
    code = ("import pulp\nfrom ortools.math_opt.python import mathopt\nm = mathopt.Model()\n"
            "x = m.add_integer_variable(lb=0, ub=3)\nm.add_linear_constraint(2 * x <= 5)\nm.maximize(x)\n"
            "mathopt.solve(m, mathopt.SolverType.HIGHS)\n")
    assert subprocess.run([sys.executable, "-c", code], capture_output=True).returncode < 0
