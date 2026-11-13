"""Lesson 12.5.4: tests of the S3 store against moto, with the fixtures a conftest.py would hold.

Run as a program, it runs its own tests with pytest and prints one line per test. No AWS is
reached. GridCap is a fictional utility.
"""

import json
import sys

import boto3
import pytest

from fake_aws import FAKE_CREDENTIALS
from gridcap import generate
from moto import mock_aws
from s3_store import Corrupted, S3Store, snapshot_key
from snapshot import export, load


@pytest.fixture
def aws_credentials(monkeypatch):
    """Fake credentials for every test, so no test can sign a request as anyone real."""
    for name, value in FAKE_CREDENTIALS.items():
        monkeypatch.setenv(name, value)


@pytest.fixture
def s3(aws_credentials):
    """A fresh, empty fake S3 per test; the client is made inside the mock."""
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture
def store(s3):
    s3.create_bucket(Bucket="gridcap-test")
    return S3Store(s3, "gridcap-test")


@pytest.fixture(scope="module")
def tiny():
    return load(json.dumps(export(generate("tiny"))))


def test_equal_content_is_one_object(store, s3, tiny):
    assert store.put_snapshot(tiny) == store.put_snapshot(tiny)
    assert s3.list_objects_v2(Bucket="gridcap-test")["KeyCount"] == 1


def test_an_overwritten_snapshot_is_refused(store, s3, tiny):
    digest = store.put_snapshot(tiny)
    s3.put_object(Bucket="gridcap-test", Key=snapshot_key(digest), Body=b'{"schema_version":1}')
    with pytest.raises(Corrupted):
        store.get_snapshot(digest)


def test_a_missing_result_is_none(store):
    assert store.get_result("results/none/run-0001.json") is None


def test_each_test_starts_with_an_empty_bucket(store, s3):
    assert s3.list_objects_v2(Bucket="gridcap-test")["KeyCount"] == 0


class Report:
    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            print(f"{report.head_line:<45} {report.outcome}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-p", "no:terminal", "-p", "no:cacheprovider"], plugins=[Report()]))
