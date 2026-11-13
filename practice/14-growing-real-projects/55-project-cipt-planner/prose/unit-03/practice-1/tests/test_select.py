"""Lesson 14.2.1: fund the most valuable projects within one budget."""

import json
import subprocess
import sys
from pathlib import Path

from cipt.data import load_request
from cipt.report import render
from cipt.solve import solve
from conftest import export, row


def test_plan_respects_the_budget():
    request = load_request(export([row("A", (300,), 90), row("B", (250,), 80), row("C", (200,), 40)],
                                  capital_budget=500))
    plan = solve(request)
    assert plan.status == "optimal"
    assert plan.funded and sum(request.project(p).capex for p in plan.funded) <= 500


def test_best_combination_beats_best_ratio():
    # A has the best value per $k, but taking it leaves no room for B and C together.
    request = load_request(export([row("A", (60,), 70), row("B", (50,), 50), row("C", (50,), 50)],
                                  capital_budget=100))
    plan = solve(request)
    assert plan.funded == ("B", "C")
    assert plan.objective == 100


def test_funds_everything_when_the_budget_allows():
    request = load_request(export([row("A", (60,), 70), row("B", (50,), 50)], capital_budget=1_000))
    assert solve(request).funded == ("A", "B")


def test_report_names_the_funded_projects():
    request = load_request(export([row("A", (60,), 70), row("B", (50,), 50), row("C", (50,), 50)],
                                  capital_budget=100))
    text = render(request, solve(request))
    assert "funded 2 of 3 projects, capex $100k of $100k, value $100k" in text


def test_command_line_prints_the_report(tmp_path):
    path = tmp_path / "export.json"
    path.write_text(json.dumps(export([row("A", (60,), 70)], capital_budget=100)))
    root = Path(__file__).resolve().parents[1]
    done = subprocess.run([sys.executable, "-m", "cipt", str(path)], cwd=root,
                          capture_output=True, text=True, check=True)
    assert done.stdout.splitlines()[0] == "test: optimal"
