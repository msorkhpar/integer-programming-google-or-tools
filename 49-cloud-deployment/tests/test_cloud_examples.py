"""The module 49 examples: the S3 store, the run index, the worker, the Batch submitter, the read-along files."""

import json
import re
import sqlite3
from pathlib import Path

import boto3
import pytest
import yaml
from moto import mock_aws

import run_index
from batch_stack import create_stack
from fake_aws import fake_aws
from gridcap import generate
from job_policy import BUCKET_ARN, allows, policy
from record_failure import handler
from s3_store import Corrupted, S3Store, result_key, snapshot_key
from settings import BadSettings, Settings
from snapshot import export, load
from solve_worker import main, run_worker
from submitter import start_run

MODULE = Path(__file__).resolve().parents[1]
SMALL = "730c8b40b1ebdabec854a5b7157ef9dd9208c223e73c7f18020d15f5a00bf520"


@pytest.fixture
def store():
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket="gridcap-test")
        yield S3Store(s3, "gridcap-test")


@pytest.fixture(scope="module")
def small():
    return load(json.dumps(export(generate("small"))))


# 12.5.1 -------------------------------------------------------------------------------------

def test_settings_report_every_problem_at_once():
    with pytest.raises(BadSettings) as caught:
        Settings.from_env({"SNAPSHOT_DIGEST": "abc", "TIME_LIMIT_S": "nan"})
    text = str(caught.value)
    assert "RESULT_BUCKET" in text and "RUN_ID" in text and "64 lowercase hex" in text and "TIME_LIMIT_S" in text


def test_the_entry_point_exits_2_on_bad_settings_and_writes_nothing(store):
    assert main({}, store.s3) == 2
    assert store.s3.list_objects_v2(Bucket="gridcap-test")["KeyCount"] == 0


# 12.5.3 -------------------------------------------------------------------------------------

def test_the_snapshot_key_is_module_46s_digest(store, small):
    assert store.put_snapshot(small) == SMALL
    assert store.s3.head_object(Bucket="gridcap-test", Key=snapshot_key(SMALL))["ContentLength"] > 0


def test_a_changed_object_is_refused_on_read(store, small):
    digest = store.put_snapshot(small)
    store.s3.put_object(Bucket="gridcap-test", Key=snapshot_key(digest), Body=b"{}")
    with pytest.raises(Corrupted):
        store.get_snapshot(digest)


def test_a_result_is_written_once(store):
    store.put_result(SMALL, "run-1", {"status": "optimal"})
    with pytest.raises(FileExistsError):
        store.put_result(SMALL, "run-1", {"status": "failed"})
    assert store.get_result(result_key(SMALL, "run-1")) == {"status": "optimal"}


def test_the_worker_solves_small_to_the_base_plan(store, small):
    digest = store.put_snapshot(small)
    key = run_worker(Settings("gridcap-test", "run-1", digest, 60), store)
    result = store.get_result(key)
    assert result["status"] == "optimal" and result["npv"] == 22741


def test_a_missing_snapshot_becomes_a_failed_result(store):
    key = run_worker(Settings("gridcap-test", "run-1", "0" * 64, 60), store)
    assert store.get_result(key)["status"] == "failed"


def test_the_index_points_at_results_and_rebuilds_from_s3(store, small, tmp_path):
    conn = run_index.connect(str(tmp_path / "runs.db"))
    run_index.create_schema(conn)
    digest = store.put_snapshot(small)
    run_index.record_submitted(conn, "run-1", digest, None)
    run_index.record_submitted(conn, "run-2", digest, None)
    assert run_index.refresh(conn, store, "run-1") == "submitted"
    run_worker(Settings("gridcap-test", "run-1", digest, 60), store)
    assert run_index.refresh(conn, store, "run-1") == "optimal"
    with pytest.raises(sqlite3.IntegrityError), conn:
        conn.execute("UPDATE run SET status = 'failed' WHERE run_id = 'run-2'")
    fresh = run_index.connect(str(tmp_path / "again.db"))
    run_index.create_schema(fresh)
    assert run_index.rebuild(fresh, store) == 1


# 12.5.2 -------------------------------------------------------------------------------------

def test_start_run_submits_one_job_with_the_run_and_digest(small, tmp_path):
    with fake_aws():
        s3, batch = boto3.client("s3"), boto3.client("batch")
        s3.create_bucket(Bucket="gridcap-test")
        stack = create_stack(boto3.client("ec2"), boto3.client("iam"), batch)
        conn = run_index.connect(str(tmp_path / "runs.db"))
        run_index.create_schema(conn)
        digest = start_run(conn, S3Store(s3, "gridcap-test"), batch, stack, "run-1", small, 60)
        job_id = conn.execute("SELECT batch_job_id FROM run").fetchone()[0]
        job = batch.describe_jobs(jobs=[job_id])["jobs"][0]
        env = {e["name"]: e["value"] for e in job["container"]["environment"]}
        assert job["jobName"] == "run-1" and env["SNAPSHOT_DIGEST"] == digest and env["TIME_LIMIT_S"] == "60"
        assert job["timeout"]["attemptDurationSeconds"] > 60


def test_the_failure_recorder_never_replaces_a_result(store, monkeypatch):
    monkeypatch.setenv("RESULT_BUCKET", "gridcap-test")
    event = {"run_id": "run-1", "snapshot_digest": SMALL, "error": {"Error": "States.TaskFailed"}}
    assert handler(event, s3=store.s3)["result_key"] == result_key(SMALL, "run-1")
    assert handler(event, s3=store.s3)["result_key"] is None


# 12.5.5 -------------------------------------------------------------------------------------

def test_the_job_policy_reads_snapshots_and_writes_results_only():
    doc = policy(BUCKET_ARN)
    assert allows(doc, "s3:GetObject", f"{BUCKET_ARN}/snapshots/sha256/x.json")
    assert allows(doc, "s3:PutObject", f"{BUCKET_ARN}/results/x/run-1.json")
    assert not allows(doc, "s3:PutObject", f"{BUCKET_ARN}/snapshots/sha256/x.json")
    assert not allows(doc, "s3:DeleteObject", f"{BUCKET_ARN}/results/x/run-1.json")


# Read-along files ---------------------------------------------------------------------------

def fences(lang: str):
    for page in sorted(MODULE.glob("README_*.md")):
        for match in re.finditer(rf"^```{lang}\n(.*?)^```", page.read_text(encoding="utf-8"), re.S | re.M):
            yield page.name, match.group(1)


def deploy_text() -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in sorted((MODULE / "deploy").rglob("*")) if p.is_file())


@pytest.mark.parametrize("lang", ["dockerfile", "yaml", "hcl", "json", "ignore", "requirements"])
def test_every_read_along_fence_is_part_of_a_deploy_file(lang):
    files = deploy_text()
    for page, body in fences(lang):
        lines = [line for line in body.splitlines() if line.strip()]
        assert all(line in files for line in lines), f"{page}: a {lang} fence is not in deploy/"


def test_the_read_along_files_parse():
    yaml.safe_load((MODULE / "deploy/compose.yaml").read_text())
    yaml.safe_load((MODULE / "deploy/github-workflows/ci.yml").read_text())
    json.loads((MODULE / "deploy/stepfunctions/solve-run.asl.json").read_text())
    json.loads((MODULE / "deploy/terraform/solve-job-policy.json").read_text())
    compose = yaml.safe_load((MODULE / "deploy/compose.yaml").read_text())
    for service in compose["services"].values():
        if "build" in service:
            assert service["build"]["labels"]["com.local.compose.project"] == "integer-programming-course"
