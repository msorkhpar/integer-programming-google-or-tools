"""The module 51 examples: each milestone's library, on GridCap small and medium (fictional data)."""

import json
import os
import time
from pathlib import Path

import pytest
from hypothesis import given, settings

from cipt_data import Corrupted, Rejected, SnapshotStore, digest, snapshot
from cipt_diagnose import conflict, message, presolve_checks
from cipt_model import Scenario, allows, build, check, npv_of, params, plan_of, solve
from cipt_properties import holds, portfolios
from cipt_trust import golden_compare, harness, run, warm_start
from cipt_value import benefit_forecast, eta_from_rul, npv_table, risk_table, value_table
from gridcap import generate, save_csv

MEDIUM_DIGEST = "df4edafe8608cd32dac97f26d0ad53e7a1e202fbb10fa232bce92bd5f3132c7a"
LOCK = Scenario(name="budget-lock", budget={2028: 40_000},
                crews={("transmission", 2029): 18, ("transmission", 2030): 18})


@pytest.fixture(scope="module")
def small():
    return generate("small")


# 13.1.1 --------------------------------------------------------------------------------------

def test_a_clean_export_is_accepted_and_its_digest_is_pinned(tmp_path):
    pf, key, warnings = snapshot(save_csv(generate("medium"), tmp_path / "medium"))
    assert key == MEDIUM_DIGEST == digest(generate("medium")) and warnings == []


def test_reordered_rows_keep_the_digest_and_a_real_change_does_not(tmp_path, small):
    folder = save_csv(small, tmp_path / "a")
    for path in folder.glob("*.csv"):
        head, *rows = path.read_text().splitlines()
        path.write_text("\n".join([head, *reversed(rows)]) + "\n")
    assert snapshot(folder)[1] == digest(small)
    text = (folder / "budgets.csv").read_text()
    (folder / "budgets.csv").write_text(text.replace(f"2027,ALL,{small.budget[2027]}", f"2027,ALL,{small.budget[2027] + 10}"))
    assert snapshot(folder)[1] != digest(small)


def test_a_bad_cell_and_a_cycle_are_both_refused(tmp_path, small):
    folder = save_csv(small, tmp_path / "a")
    text = (folder / "projects.csv").read_text()
    (folder / "projects.csv").write_text(text.replace(",Ridge,", ",Rigde,", 1))
    with pytest.raises(Rejected) as cell:
        snapshot(folder)
    assert [f.rule for f in cell.value.findings] == ["unknown-code"]
    folder = save_csv(small, tmp_path / "b")
    lines = (folder / "projects.csv").read_text().splitlines()
    rows = [line.split(",") for line in lines]
    idx = rows[0].index("parent")
    rows[1][idx], rows[2][idx] = rows[2][0], rows[1][0]
    (folder / "projects.csv").write_text("\n".join(",".join(r) for r in rows) + "\n")
    with pytest.raises(Rejected) as cycle:
        snapshot(folder)
    assert [f.rule for f in cycle.value.findings if f.severity == "error"] == ["parent-cycle"]


def test_the_store_refuses_an_edited_file(tmp_path, small):
    store = SnapshotStore(tmp_path / "store")
    key = store.put(small)
    assert store.put(small) == key and store.get(key) == small
    path = tmp_path / "store" / f"{key}.json"
    path.write_bytes(path.read_bytes().replace(b'"2027":', b'"2027": ', 1))
    with pytest.raises(Corrupted):
        store.get(key)


# 13.1.2 --------------------------------------------------------------------------------------

def test_small_solves_to_the_reference_and_its_plan_breaks_nothing(small):
    b = build(small)
    result = solve(b.model)
    plan = plan_of(b, result)
    assert result.objective_value() == pytest.approx(17_463) and npv_of(small, plan) == 17_463
    assert check(small, b.scenario, plan) == [] and allows(b, plan)


def test_the_medium_model_has_every_row_family():
    b = build(generate("medium"))
    assert len(b.x) == 887 and len(b.rules) == 543


def test_model_and_checker_agree_on_refused_plans(small):
    b = build(small)
    plan = plan_of(b, solve(b.model))
    must = next(p.project_id for p in small.projects if p.must_do)
    dropped = {k: v for k, v in plan.items() if k != must}
    assert not allows(b, dropped) and f"must_{must}" in check(small, b.scenario, dropped)
    assert not allows(b, {**plan, must: 1900})


# 13.1.3 --------------------------------------------------------------------------------------

def test_the_npv_table_is_gridcaps_own():
    pf, forecast = benefit_forecast("small")
    table = npv_table(pf, forecast)
    assert all(table[p.project_id, t] == p.npv[t] for p in pf.projects for t in p.starts())


def test_an_anchored_eta_makes_the_rul_the_median():
    import math
    a = generate("medium").asset("A086")
    eta = eta_from_rul(a.age, a.rul, a.weibull_beta)
    survive = math.exp(-((a.age + a.rul) / eta) ** a.weibull_beta) / math.exp(-(a.age / eta) ** a.weibull_beta)
    assert survive == pytest.approx(0.5)


def test_value_is_linear_in_its_measures(small):
    npv = {(p.project_id, t): p.npv[t] for p in small.projects for t in p.starts()}
    rr = risk_table(small)
    v = value_table(npv, rr)
    key = next(iter(v))
    assert v[key] == pytest.approx(0.375 * npv[key] / 5000 + 0.625 * rr[key] / 2000)


# 13.1.4 --------------------------------------------------------------------------------------

def test_the_budget_lock_conflict_is_the_four_rows():
    medium = generate("medium")
    assert presolve_checks(medium, LOCK) == []
    found = conflict(build(medium, LOCK))
    assert found.rows == ["crews_transmission_2029", "crews_transmission_2030", "must_P097", "must_P370"]
    text = message(build(medium, LOCK))
    assert "19 transmission crew-months in 2029 instead of 18" in text


def test_a_typo_is_stopped_before_the_filter():
    text = message(build(generate("medium"), Scenario(name="t", budget={2027: 428})))
    assert "Pre-solve checks failed" in text and "required-over-budget: 2027" in text


# 13.1.5 --------------------------------------------------------------------------------------

def test_a_manifest_repeats_and_matches_the_golden_record():
    golden = json.loads((Path(__file__).resolve().parents[1] / "src/golden/cipt_golden.json").read_text())
    first = run({"size": "small", "gap": 0.0})
    assert golden_compare(golden["small-base"], first) == []
    _, key = harness({"size": "small", "gap": 0.0}, runs=3)
    assert len(key) == 64


def test_the_golden_compare_names_a_tie():
    manifest = run({"size": "small", "gap": 0.0})
    record = {"snapshot": manifest["inputs"]["snapshot"], "status": "OPTIMAL",
              "objective": manifest["result"]["objective"], "plan_digest": "000000000000"}
    assert golden_compare(record, manifest) == [f"plan 000000000000 -> {manifest['result']['plan_digest']} (same value: a tie)"]


@settings(max_examples=25, derandomize=True, database=None, deadline=None)
@given(portfolios())
def test_properties_hold_on_drawn_portfolios(case):
    holds(case)


def test_a_repaired_start_breaks_nothing(small):
    b = build(small, Scenario(name="cut", budget={2028: 6_000}))
    base = build(small)
    last = plan_of(base, solve(base.model))
    _, start = warm_start(b, last)
    assert check(small, b.scenario, start) == []


# 13.1.6 --------------------------------------------------------------------------------------

def test_the_service_runs_a_job_offline(tmp_path, monkeypatch):
    for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
        monkeypatch.setenv(name, "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    import boto3
    from fastapi.testclient import TestClient
    from moto import mock_aws

    from cipt_service import JobTable, S3Store, create_app
    with mock_aws():
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="cipt-test")
        client = TestClient(create_app(S3Store(s3, "cipt-test"), JobTable(tmp_path / "jobs.sqlite")))
        snap = client.post("/snapshots", json=generate("small").to_dict()).json()["snapshot"]
        job = client.post("/jobs", json={"snapshot": snap, "gap": 0.0}).json()["job_id"]
        while not client.get(f"/jobs/{job}").json()["finished"]:
            time.sleep(0.02)
        assert client.get(f"/jobs/{job}/result").json()["npv"] == pytest.approx(17_463)
        assert client.get("/jobs/nope").status_code == 404
        points = client.post("/frontier", json={"snapshot": snap, "points": 3, "gap": 0.0}).json()["points"]
        assert all(not (q["npv"] >= p["npv"] and q["risk"] >= p["risk"] and q != p) for p in points for q in points)
