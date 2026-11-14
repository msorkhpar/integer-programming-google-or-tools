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

import json
import tempfile

from trim_index import best_runs, connect, poll, record, result_key

survey_a, survey_b = "c" * 64, "d" * 64

with mock_aws(), tempfile.TemporaryDirectory() as folder:
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="runs-demo")
    conn = connect(os.path.join(folder, "runs.db"))
    for run_id, digest in (("r-10", survey_a), ("r-11", survey_a), ("r-12", survey_b)):
        record(conn, run_id, digest)
    for run_id, digest, body in (("r-10", survey_a, {"status": "time_limit", "cost": 520}),
                                 ("r-11", survey_a, {"status": "optimal", "cost": 480}),
                                 ("r-12", survey_b, {"status": "infeasible"})):
        s3.put_object(Bucket="runs-demo", Key=result_key(digest, run_id), Body=json.dumps(body).encode())
    record(conn, "r-13", survey_b)
    for run_id in ("r-10", "r-11", "r-12", "r-13", "r-99"):
        print(f"poll {run_id}:", poll(conn, s3, "runs-demo", run_id))
    print("best runs:", {d[:4]: r for d, r in best_runs(conn).items()})
    conn.close()
