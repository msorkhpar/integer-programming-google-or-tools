"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import os

for library in ("boto3", "botocore", "moto", "urllib3", "werkzeug"):
    logging.getLogger(library).setLevel(logging.WARNING)
for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

import boto3  # noqa: E402
from moto import mock_aws  # noqa: E402

from s3_store import Corrupted, NotStored, canonical, get_snapshot, put_snapshot  # noqa: E402

snapshot = {
    "years": [2031], "rate": 0.04, "budget": {2031: 500},
    "region_budget": {"East": {2031: 300}}, "crews": {"lines": {2031: 4}}, "floor": {"East": 50},
    "projects": {"K1": {"cost": [120], "earliest": 2031, "latest": 2031, "npv": {2031: 66}}},
}

with mock_aws():
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="demo-snapshots")
    digest = put_snapshot(s3, "demo-snapshots", snapshot)
    print("digest:", digest)
    print("digest of a second put:", put_snapshot(s3, "demo-snapshots", snapshot))
    print("read back equal:", get_snapshot(s3, "demo-snapshots", digest) == snapshot)
    s3.put_object(Bucket="demo-snapshots", Key=f"snapshots/{digest}.json", Body=b"{}")
    for key in (digest, "0" * 64):
        try:
            get_snapshot(s3, "demo-snapshots", key)
            print(f"read {key[:8]}: no error")
        except (Corrupted, NotStored) as error:
            print(f"read {key[:8]}:", type(error).__name__, error)
