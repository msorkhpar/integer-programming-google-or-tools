"""Lesson 14.2.7: scenarios as data, overrides as named rows, snapshots and runs in SQLite."""

import hashlib
import json
import sqlite3

import pytest

from cipt.data import load_request
from cipt.diagnose import why_infeasible
from cipt.scenario import Scenario, apply, diff
from cipt.solve import solve
from cipt.store import Store
from conftest import export, row

TWO = (2027, 2028)


def base():
    return export([row("A", (100,), {2027: 300, 2028: 250}, latest=2028), row("B", (100,), 200, latest=2028),
                   row("C", (100,), 50, latest=2028)], years=TWO, budget={2027: 100, 2028: 100})


def plan_for(scenario):
    return solve(apply(load_request(base()), scenario))


def test_force_out_drops_a_project():
    assert plan_for(Scenario("no A", force_out=("A",))).funded == ("B", "C")


def test_force_in_funds_a_low_value_project():
    assert plan_for(Scenario("C first", force_in=("C",))).funded == ("A", "C")


def test_fix_start_pins_the_year():
    assert plan_for(Scenario("A late", fix_start={"A": 2028})).starts["A"] == 2028


def test_budget_change_replaces_one_year():
    plan = plan_for(Scenario("cut", budget={2028: 0}))
    assert plan.starts == {"A": 2027}


def test_clashing_override_is_named_in_the_conflict():
    raw = export([row("A", (10,), 5, must_do=True, alt_group="G"), row("B", (10,), 5, alt_group="G")])
    conflict = why_infeasible(apply(load_request(raw), Scenario("both", force_in=("B",))))
    assert (conflict.rows if conflict else None) == ["alt_G", "in_B", "must_A"]


def test_diff_reports_selected_deferred_and_shifted():
    d = diff(plan_for(Scenario("base")), plan_for(Scenario("C first", force_in=("C",))))
    assert (d.selected, d.deferred) == (("C",), ("B",))


def test_snapshot_is_stored_under_its_hash(tmp_path):
    store = Store(tmp_path / "cipt.db")
    digest = store.save_snapshot(base())
    canonical = json.dumps(base(), sort_keys=True, separators=(",", ":"))
    assert digest == hashlib.sha256(canonical.encode()).hexdigest()
    assert store.snapshot(digest) == base()


def test_changed_snapshot_is_refused(tmp_path):
    store = Store(tmp_path / "cipt.db")
    digest = store.save_snapshot(base())
    with sqlite3.connect(tmp_path / "cipt.db") as db:
        db.execute("UPDATE snapshot SET body = replace(body, '300', '900')")
    with pytest.raises(ValueError, match="does not match"):
        store.snapshot(digest)


def test_run_is_stored_and_read_back(tmp_path):
    store = Store(tmp_path / "cipt.db")
    store.save_scenario(Scenario("no A", force_out=("A",), note="A is on hold"), store.save_snapshot(base()))
    plan = store.run("no A")
    again = Store(tmp_path / "cipt.db")
    assert [(p.funded, p.npv) for p in again.runs("no A")] == [(("B", "C"), 250)] == [(plan.funded, plan.npv)]
