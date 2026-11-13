import os

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from run_listing import runs_of

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(Bucket="trim-test")
        yield client


def put(s3, *keys):
    for key in keys:
        s3.put_object(Bucket="trim-test", Key=key, Body=b"{}")


def test_the_runs_of_a_survey_are_listed_and_an_empty_survey_has_none(s3):
    put(s3, "trim-results/S-7/t-2.json", "trim-results/S-7/t-1.json", "trim-results/S-9/t-3.json")
    assert runs_of(s3, "trim-test", "S-7") == ["t-1", "t-2"]
    assert runs_of(s3, "trim-test", "S-8") == []


def test_more_than_1000_results_are_all_listed(s3):
    put(s3, *[f"trim-results/S-7/t-{i:04d}.json" for i in range(1003)])
    runs = runs_of(s3, "trim-test", "S-7")
    assert len(runs) == 1003 and runs[-1] == "t-1002"


def test_a_survey_id_that_starts_another_is_not_mixed_in(s3):
    put(s3, "trim-results/S-7/t-1.json", "trim-results/S-70/t-5.json")
    assert runs_of(s3, "trim-test", "S-7") == ["t-1"]


def test_only_result_files_count(s3):
    put(s3, "trim-results/S-7/t-1.json", "trim-results/S-7/t-1.log", "trim-results/S-7/old/t-0.json")
    assert runs_of(s3, "trim-test", "S-7") == ["t-1"]


def test_a_missing_bucket_raises_instead_of_listing_nothing(s3):
    try:
        found, code = runs_of(s3, "no-such-trim", "S-7"), None
    except ClientError as error:
        found, code = None, error.response["Error"]["Code"]
    assert (found, code) == (None, "NoSuchBucket")
