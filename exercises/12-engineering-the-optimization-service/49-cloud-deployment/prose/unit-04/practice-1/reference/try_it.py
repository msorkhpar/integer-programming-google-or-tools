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

from run_listing import runs_of

with mock_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="runs-demo")
    keys = ["trim-results/V-4/r-b.json", "trim-results/V-4/r-a.json", "trim-results/V-4/logs/r-a.json",
            "trim-results/V-4/r-a.log", "trim-results/V-40/r-z.json"]
    keys += [f"trim-results/V-6/r-{i:04d}.json" for i in range(1004)]
    for key in keys:
        s3.put_object(Bucket="runs-demo", Key=key, Body=b"{}")
    print("runs of V-4:", runs_of(s3, "runs-demo", "V-4"))
    print("runs of V-5:", runs_of(s3, "runs-demo", "V-5"))
    print("how many runs of V-6:", len(runs_of(s3, "runs-demo", "V-6")))
