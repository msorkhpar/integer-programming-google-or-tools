"""Lesson 14.2.6: why a request has no plan, and why a project was deferred."""

import json
import subprocess
import sys
from pathlib import Path

from cipt.data import load_request
from cipt.diagnose import why_deferred, why_infeasible
from cipt.solve import solve
from conftest import export, row

TWO = (2027, 2028)


def musts_over_budget():
    return export([row("A", (100,), 5, must_do=True), row("B", (100,), 5, must_do=True), row("C", (10,), 50),
                   row("D", (10,), 1, alt_group="G"), row("E", (10,), 2, alt_group="G")], capital_budget=150)


def test_conflict_names_the_clashing_rules():
    conflict = why_infeasible(load_request(musts_over_budget()))
    assert (conflict.rows if conflict else None) == ["budget_2027", "must_A", "must_B"]


def test_conflict_leaves_out_rules_that_do_not_clash():
    raw = export([row("A", (100,), 5, must_do=True), row("B", (10,), 5, latest=2028, alt_group="G"),
                  row("C", (10,), 5, latest=2028, alt_group="G")], years=TWO, budget={2027: 50, 2028: 1000})
    conflict = why_infeasible(load_request(raw))
    assert (conflict.rows if conflict else None) == ["budget_2027", "must_A"]


def test_message_states_each_rule_in_planners_words():
    conflict = why_infeasible(load_request(musts_over_budget()))
    message = conflict.message if conflict else ""
    assert "  must_A: A is a must-do" in message
    assert "  budget_2027: spend in 2027 within $150k" in message


def test_deferral_prices_forcing_a_project_in():
    request = load_request(export([row("A", (100,), 300), row("B", (100,), 200)], capital_budget=100))
    d = why_deferred(request, solve(request), "B")
    assert (d.npv_cost, d.displaced, d.conflict) == (100, ("A",), None)


def test_deferral_names_the_rows_that_block_it():
    # B needs P started a year earlier, and P cannot start before 2027.
    request = load_request(export([row("P", (10,), 5), row("B", (10,), 9, parent="P", lag=1)]))
    d = why_deferred(request, solve(request), "B")
    assert (d.conflict.rows if d.conflict else None) == ["after_B_2027", "force_B"]


def test_command_line_explains_an_infeasible_request(tmp_path):
    path = tmp_path / "export.json"
    path.write_text(json.dumps(musts_over_budget()))
    done = subprocess.run([sys.executable, "-m", "cipt", str(path)], cwd=Path(__file__).resolve().parents[1],
                          capture_output=True, text=True)
    assert "No plan meets these 3 rules together" in done.stdout


def test_message_words_alternatives_and_the_risk_floor():
    # Forcing B in clashes with A's group in the first export and with the risk floor in the second.
    big = {"id": "A-big", "age": 10, "weibull_beta": 2.0, "weibull_eta": 30.0, "cof": 100_000}
    group = export([row("A", (10,), 5, must_do=True, alt_group="G"), row("B", (10,), 9, alt_group="G")])
    floor = export([row("A", (10,), 5, asset=big), row("B", (10,), 9)], years=TWO,
                   budget={2027: 10, 2028: 10}, risk_floor=1000)
    deferrals = [why_deferred(request, solve(request), "B") for request in map(load_request, (group, floor))]
    messages = [d.conflict.message if d.conflict else "" for d in deferrals]
    assert "  alt_G: at most one of A, B" in messages[0]
    assert "  risk_floor: remove at least $1,000.0k of risk" in messages[1]


def test_why_adds_nothing_for_a_funded_project(tmp_path):
    path = tmp_path / "export.json"
    path.write_text(json.dumps(export([row("A", (50,), 300), row("B", (100,), 200)], capital_budget=100)))
    root = Path(__file__).resolve().parents[1]
    plain, why = (subprocess.run([sys.executable, "-m", "cipt", str(path), *extra], cwd=root,
                                 capture_output=True, text=True) for extra in ([], ["--why", "A"]))
    assert (why.returncode, why.stdout) == (0, plain.stdout)
