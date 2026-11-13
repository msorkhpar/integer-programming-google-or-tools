import hashlib
import os

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws

from survey_store import get_survey, put_survey, survey_key

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

SURVEY = {"survey_id": "S-2031-07", "region": "Coast",
          "readings": [{"asset_id": "T-114", "condition": 3}, {"asset_id": "P-020", "condition": 5}]}


@pytest.fixture
def s3():
    with mock_aws():
        client = boto3.client("s3")
        client.create_bucket(Bucket="surveys-test")
        yield client


def count(s3):
    return s3.list_objects_v2(Bucket="surveys-test").get("KeyCount", 0)


def test_a_survey_is_stored_under_its_digest_and_read_back(s3):
    digest = put_survey(s3, "surveys-test", SURVEY)
    assert len(digest) == 64 and count(s3) == 1
    body = s3.get_object(Bucket="surveys-test", Key=survey_key(digest))["Body"].read()
    assert hashlib.sha256(body).hexdigest() == digest
    survey, status = get_survey(s3, "surveys-test", digest)
    assert status == "ok" and survey["survey_id"] == "S-2031-07"


def test_equal_content_in_another_order_is_one_object(s3):
    shuffled = {"readings": list(reversed(SURVEY["readings"])), "region": "Coast", "survey_id": "S-2031-07"}
    first, second = put_survey(s3, "surveys-test", SURVEY), put_survey(s3, "surveys-test", shuffled)
    assert first == second and len(first) == 64 and count(s3) == 1


def test_a_put_never_replaces_an_existing_object(s3):
    digest = put_survey(s3, "surveys-test", SURVEY)
    s3.put_object(Bucket="surveys-test", Key=survey_key(digest), Body=b'{"edited":true}')
    assert put_survey(s3, "surveys-test", SURVEY) == digest
    assert get_survey(s3, "surveys-test", digest) == (None, "corrupted")


def test_a_changed_object_is_reported_corrupted(s3):
    digest = put_survey(s3, "surveys-test", SURVEY)
    s3.put_object(Bucket="surveys-test", Key=survey_key(digest), Body=b'{"edited":true}')
    assert get_survey(s3, "surveys-test", digest) == (None, "corrupted")


def test_a_missing_survey_is_reported_missing(s3):
    put_survey(s3, "surveys-test", SURVEY)
    assert get_survey(s3, "surveys-test", "0" * 64) == (None, "missing")


def test_a_missing_bucket_is_an_error_not_a_success(s3):
    try:
        digest, code = put_survey(s3, "no-such-surveys", SURVEY), None
    except ClientError as error:
        digest, code = None, error.response["Error"]["Code"]
    assert (digest, code) == (None, "NoSuchBucket")
