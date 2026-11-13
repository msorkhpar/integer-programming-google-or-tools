"""The module 45 examples: scenarios as data, overrides with an audit trail, cycle states, the SQLite store."""

import copy
import sqlite3
from contextlib import closing

import pytest

import store
from cycle import Refused, Service
from gridcap import generate
from overrides import Override, check, replay, request, revoke
from scenario import Scenario, copy_scenario, create, diff_plans, optimize


@pytest.fixture(scope="module")
def small():
    return generate("small")


@pytest.fixture
def base(small):
    return create(small, "small", "S-001", "base", by="planner-a", at="2027-03-01T09:00Z")


def test_metadata_is_not_an_input(base):
    renamed = copy.deepcopy(base)
    renamed.name, renamed.created_by = "other", "planner-b"
    assert renamed.snapshot() == base.snapshot()
    renamed.budget[2030] -= 1
    assert renamed.snapshot() != base.snapshot()


def test_json_round_trip(base):
    base.overrides["P032"] = Override("P032", "out")
    again = Scenario.from_json(base.to_json())
    assert again == base and again.snapshot() == base.snapshot()


def test_copy_shares_nothing_mutable(base):
    cut = copy_scenario(base, "S-002", "cut", by="planner-b", at="t")
    cut.budget[2030] = 1
    assert base.budget[2030] == 8610 and cut.parent_id == "S-001"
    assert copy.copy(base).budget is base.budget


def test_base_and_cut_plans(base):
    cut = copy_scenario(base, "S-002", "cut", by="planner-b", at="t")
    cut.budget[2030] = 7750
    a, b = optimize(base), optimize(cut)
    assert (a.npv, len(a.starts), b.npv) == (24260, 27, 23887)
    assert diff_plans(a, b) == {"selected": ["P006"], "deferred": ["P016"], "shifted": ["P018 2030->2031"]}


def test_override_checks(small):
    assert check(Override("P038", "start_in", 2029), small) == ["P038 cannot start in 2029: its window is 2027-2027"]
    assert check(Override("P017", "out"), small) == ["P017 is a must-do and cannot be overridden out"]
    assert check(Override("P024", "start_in", 2029), small) == []


def test_trail_replays_supersede_and_revoke(small, base):
    trail = []
    request(base, trail, Override("P024", "start_in", 2029), small, "planner-a", "t1", "w")
    e = request(base, trail, Override("P024", "start_in", 2030), small, "planner-a", "t2", "w")
    assert e.changes == ("x_P024_2029 [1,1] -> [0,0]", "x_P024_2030 [0,0] -> [1,1]")
    request(base, trail, Override("P021", "not_before", 2030), small, "planner-c", "t3", "w")
    revoke(base, trail, "P021", small, "manager-a", "t4", "w")
    assert replay(trail, "S-001") == base.overrides == {"P024": Override("P024", "start_in", 2030)}


def test_three_overrides_cost(base):
    s = copy_scenario(base, "S-002", "q2", by="planner-a", at="t")
    s.overrides = {o.project: o for o in [Override("P024", "start_in", 2030), Override("P032", "out"),
                                         Override("P036", "not_before", 2029)]}
    r = optimize(s)
    assert r.npv == 22989 and r.starts["P024"] == 2030 and "P032" not in r.starts and r.starts.get("P036", 2029) >= 2029


def test_forced_2027_starts_are_infeasible(base):
    s = copy_scenario(base, "S-003", "early", by="planner-a", at="t")
    s.overrides = {p: Override(p, "start_in", 2027) for p in ("P032", "P034", "P038")}
    assert optimize(s).status == "INFEASIBLE"
    for drop in s.overrides:
        trial = copy.deepcopy(s)
        del trial.overrides[drop]
        assert optimize(trial).status == "OPTIMAL"


def test_cycle_refusals(base):
    svc = Service()
    svc.add(base, "2027 plan")
    with pytest.raises(Refused):
        svc.start_run("S-001")
    a, _, v = svc.read("S-001")
    svc.edit("S-001", v, a)
    with pytest.raises(Refused, match="version 2, not 1"):
        svc.edit("S-001", v, a)
    v = svc.check("S-001", 2)
    t = svc.start_run("S-001")
    s, _, v = svc.read("S-001")
    v = svc.edit("S-001", v, s)
    with pytest.raises(Refused):
        svc.finish_run(t, optimize(t.inputs))


def test_sqlite_store_rules(small, base, tmp_path):
    with closing(store.connect(str(tmp_path / "s.db"))) as conn:
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        store.create_schema(conn)
        store.add(conn, base, "2027 plan")
        store.check_inputs(conn, "S-001", 1)
        t = store.start_run(conn, "S-001")
        store.save_run(conn, t, optimize(t.inputs))
        store.lock(conn, "S-001", 3)
        with pytest.raises(sqlite3.IntegrityError, match="locked"):
            conn.execute("UPDATE scenario SET name = 'x' WHERE scenario_id = 'S-001'")
        conn.rollback()
        store.copy(conn, "S-001", "S-002", "c", by="planner-b", at="t")
        v = store.request(conn, "S-002", 1, Override("P032", "out"), small, "planner-b", "t", "w")
        with pytest.raises(store.Refused):
            store.request(conn, "S-002", 1, Override("P024", "out"), small, "planner-b", "t", "w")
        assert v == 2 and [e.override.project for e in store.trail(conn, "S-002")] == ["P032"]
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM audit")
