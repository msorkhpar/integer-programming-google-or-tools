"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import os

import boto3
from moto import mock_aws

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
for noisy in ("botocore", "boto3", "urllib3", "moto", "s3transfer"):
    logging.getLogger(noisy).setLevel(logging.WARNING)

from survey_store import get_survey, put_survey, survey_key

survey = {"survey_id": "S-2035-02", "region": "Valley",
          "readings": [{"asset_id": "V-9", "condition": 2}, {"asset_id": "A-1", "condition": 4}]}

with mock_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="surveys-demo")
    digest = put_survey(s3, "surveys-demo", survey)
    again = put_survey(s3, "surveys-demo", {**survey, "readings": survey["readings"][::-1]})
    print("digest:", digest[:16])
    print("readings reversed, same digest:", again == digest)
    print("objects stored:", s3.list_objects_v2(Bucket="surveys-demo").get("KeyCount", 0))
    print("read back:", get_survey(s3, "surveys-demo", digest))
    print("digest 0...0:", get_survey(s3, "surveys-demo", "0" * 64))
    if digest:
        s3.put_object(Bucket="surveys-demo", Key=survey_key("f" * 64), Body=b"{}")
    print("digest f...f holding other bytes:", get_survey(s3, "surveys-demo", "f" * 64))
