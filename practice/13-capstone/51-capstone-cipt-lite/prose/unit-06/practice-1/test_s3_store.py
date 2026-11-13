import copy
import hashlib
import os

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SECURITY_TOKEN", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"                     # moto's fake credentials: no real account is used
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import boto3                                          # noqa: E402
import pytest                                         # noqa: E402
from moto import mock_aws                             # noqa: E402

from s3_store import Corrupted, NotStored, canonical, get_snapshot, put_snapshot   # noqa: E402

BUCKET = "practice-snapshots"
SNAPSHOT = {
    "years": [2027, 2028], "rate": 0.05,
    "budget": {2027: 400, 2028: 350},
    "region_budget": {"North": {2027: 250, 2028: 200}, "South": {2027: 250, 2028: 200}},
    "crews": {"lines": {2027: 3, 2028: 3}, "poles": {2027: 2, 2028: 2}},
    "floor": {"North": 100, "South": 0},
    "projects": {
        "J1": {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027, "latest": 2027,
               "must": True, "parent": None, "lag": 0, "group": None, "crews": 2, "npv": {2027: 90}},
        "J2": {"program": "poles", "region": "South", "cost": [120], "earliest": 2027, "latest": 2028,
               "must": False, "parent": "J1", "lag": 1, "group": None, "crews": 1, "npv": {2027: 40, 2028: 38}},
    },
}


class Counting:
    """An S3 client that counts its put_object calls."""

    def __init__(self, client):
        self.client, self.puts = client, 0

    def put_object(self, **kwargs):
        self.puts += 1
        return self.client.put_object(**kwargs)

    def __getattr__(self, name):
        return getattr(self.client, name)


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield Counting(client)


def test_a_snapshot_is_stored_under_its_digest_and_read_back(s3):
    digest = put_snapshot(s3, BUCKET, SNAPSHOT)
    assert digest == hashlib.sha256(canonical(SNAPSHOT)).hexdigest()
    keys = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET).get("Contents", [])]
    assert keys == [f"snapshots/{digest}.json"]
    back = get_snapshot(s3, BUCKET, digest)
    assert back.get("budget") == SNAPSHOT["budget"] and sorted(back.get("projects", {})) == ["J1", "J2"]


def test_storing_the_same_content_twice_writes_once(s3):
    first = put_snapshot(s3, BUCKET, SNAPSHOT)
    second = put_snapshot(s3, BUCKET, copy.deepcopy(SNAPSHOT))
    assert first == second and s3.puts == 1


def test_the_digest_does_not_depend_on_key_order():
    reordered = {key: SNAPSHOT[key] for key in reversed(list(SNAPSHOT))}
    assert canonical(reordered) == canonical(SNAPSHOT) != b""


def test_an_object_edited_in_place_is_refused(s3):
    digest = put_snapshot(s3, BUCKET, SNAPSHOT)
    assert digest, "put_snapshot returned no digest"
    key = f"snapshots/{digest}.json"
    body = s3.get_object(Bucket=BUCKET, Key=key)["Body"].read().replace(b'"2028":350', b'"2028":900')
    s3.client.put_object(Bucket=BUCKET, Key=key, Body=body)
    try:
        get_snapshot(s3, BUCKET, digest)
        caught = None
    except Corrupted as error:
        caught = error
    assert isinstance(caught, Corrupted)


def test_every_year_key_comes_back_as_an_integer(s3):
    digest = put_snapshot(s3, BUCKET, SNAPSHOT)
    assert digest, "put_snapshot returned no digest"
    assert get_snapshot(s3, BUCKET, digest) == SNAPSHOT


def test_a_digest_never_stored_is_not_stored_not_a_client_error(s3):
    try:
        get_snapshot(s3, BUCKET, "0" * 64)
        caught = None
    except Exception as error:
        caught = error
    assert isinstance(caught, NotStored)
