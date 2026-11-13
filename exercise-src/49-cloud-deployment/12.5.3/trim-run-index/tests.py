import json
import os

import boto3
import pytest
from moto import mock_aws

from trim_index import best_runs, connect, poll, record, result_key

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

A, B = "a" * 64, "b" * 64


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(Bucket="trim-test")
        yield client


@pytest.fixture
def conn(tmp_path):
    return connect(str(tmp_path / "trim.db"))


def finish(s3, digest, run_id, status, cost=None):
    body = {"run_id": run_id, "status": status, **({"cost": cost} if cost is not None else {})}
    s3.put_object(Bucket="trim-test", Key=result_key(digest, run_id), Body=json.dumps(body).encode())


def test_a_poll_records_a_finished_run(conn, s3):
    record(conn, "t-1", A)
    finish(s3, A, "t-1", "optimal", 410)
    assert poll(conn, s3, "trim-test", "t-1") == "optimal"
    row = conn.execute("SELECT status, result_key, cost FROM run").fetchone()
    assert tuple(row) == ("optimal", result_key(A, "t-1"), 410)


def test_a_run_without_a_result_stays_submitted(conn, s3):
    record(conn, "t-1", A)
    finish(s3, A, "t-1", "optimal", 410)
    record(conn, "t-2", A)
    assert [poll(conn, s3, "trim-test", r) for r in ("t-1", "t-2")] == ["optimal", "submitted"]


def test_a_recorded_run_is_not_read_again(conn, s3):
    record(conn, "t-1", A)
    finish(s3, A, "t-1", "optimal", 410)
    poll(conn, s3, "trim-test", "t-1")
    s3.delete_object(Bucket="trim-test", Key=result_key(A, "t-1"))
    assert poll(conn, s3, "trim-test", "t-1") == "optimal"


def test_an_unknown_run_is_unknown(conn, s3):
    record(conn, "t-1", A)
    assert poll(conn, s3, "trim-test", "t-9") == "unknown"


def test_the_best_run_has_a_plan_and_the_lowest_cost(conn, s3):
    for run_id, status, cost in [("t-1", "time_limit", 520), ("t-4", "optimal", 480)]:
        record(conn, run_id, A)
        finish(s3, A, run_id, status, cost)
        poll(conn, s3, "trim-test", run_id)
    assert best_runs(conn) == {A: "t-4"}


def test_infeasible_and_failed_runs_are_never_best(conn, s3):
    record(conn, "t-1", A)
    finish(s3, A, "t-1", "infeasible")
    record(conn, "t-2", A)
    finish(s3, A, "t-2", "time_limit", 900)
    for run_id in ("t-1", "t-2"):
        poll(conn, s3, "trim-test", run_id)
    assert best_runs(conn) == {A: "t-2"}


def test_each_survey_gets_its_own_best_run_and_ties_go_to_the_lower_id(conn, s3):
    for run_id, digest, cost in [("t-2", A, 300), ("t-1", A, 300), ("t-3", B, 700)]:
        record(conn, run_id, digest)
        finish(s3, digest, run_id, "optimal", cost)
        poll(conn, s3, "trim-test", run_id)
    assert best_runs(conn) == {A: "t-1", B: "t-3"}
