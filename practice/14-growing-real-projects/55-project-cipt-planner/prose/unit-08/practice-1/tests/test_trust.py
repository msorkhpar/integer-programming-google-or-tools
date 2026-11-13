"""Lesson 14.2.8: a manifest per run, a determinism harness, a golden plan and warm starts."""

import json
from pathlib import Path

from cipt.data import load_request
from cipt.model import build
from cipt.plan import Plan
from cipt.scenario import Scenario
from cipt.solve import hint_values, solve
from cipt.store import content_hash
from cipt.trust import check_golden, harness, manifest, plan_digest, warm_solve
from conftest import export, row

TWO = (2027, 2028)
GOLDEN = Path(__file__).parent / "golden" / "demo_plan.json"
DEMO = Path(__file__).resolve().parents[1] / "data" / "demo.json"


def base():
    return export([row("A", (100,), {2027: 300, 2028: 250}, latest=2028), row("B", (100,), 200, latest=2028),
                   row("C", (100,), 50, latest=2028)], years=TWO, budget={2027: 100, 2028: 100})


def test_harness_finds_identical_runs():
    h = harness(base(), runs=3)
    assert (len(h.digests), h.same) == (3, True)


def test_plan_digest_changes_with_the_plan():
    a, b = Plan("optimal", {"A": 2027}), Plan("optimal", {"A": 2028})
    assert plan_digest(a) == plan_digest(Plan("optimal", {"A": 2027})) != plan_digest(b)


def test_manifest_records_the_input_and_the_settings():
    plan = solve(load_request(base()))
    m = manifest(base(), Scenario("base"), plan)
    assert (m.get("input"), m.get("plan"), m.get("solver", {}).get("threads")) == \
        (content_hash(base()), plan_digest(plan), 1)


def test_golden_check_reports_each_changed_start(tmp_path):
    golden = tmp_path / "golden.json"
    golden.write_text(json.dumps({"input": content_hash(base()), "status": "optimal", "npv": 500,
                                  "starts": {"A": 2027, "C": 2028}}))
    assert check_golden(base(), golden) == ["B: start None -> 2028", "C: start 2028 -> None"]


def test_golden_check_refuses_a_changed_input(tmp_path):
    golden = tmp_path / "golden.json"
    golden.write_text(json.dumps({"input": "0" * 64, "status": "optimal", "npv": 500, "starts": {}}))
    assert check_golden(base(), golden) == [f"input changed: golden {'0' * 12}, now {content_hash(base())[:12]}"]


def test_demo_plan_matches_its_golden():
    assert check_golden(json.loads(DEMO.read_text()), GOLDEN) == []


def test_hint_keeps_only_starts_this_model_has():
    built = build(load_request(base()))
    values = hint_values(built, Plan("optimal", {"A": 2026, "B": 2028, "Z": 2027}))
    assert {k for k, v in values.items() if v == 1} == {("B", 2028)}


def test_warm_start_gives_the_cold_plan():
    last = Plan("optimal", {"B": 2027, "C": 2028})
    assert warm_solve(base(), last).starts == solve(load_request(base())).starts == {"A": 2027, "B": 2028}
