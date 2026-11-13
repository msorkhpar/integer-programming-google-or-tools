"""Lesson 12.5.1: the container's command, called the way Batch starts it: environment in, exit code out.

S3 is moto's fake (no AWS is reached). The first call has every setting; the second is a container
started without its bucket. GridCap is a fictional utility.
"""

import json

import boto3

from fake_aws import fake_aws
from gridcap import generate
from s3_store import S3Store
from snapshot import export, load
from solve_worker import main

with fake_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="gridcap-runs-example")
    digest = S3Store(s3, "gridcap-runs-example").put_snapshot(load(json.dumps(export(generate("small")))))
    env = {"RESULT_BUCKET": "gridcap-runs-example", "RUN_ID": "run-0007", "SNAPSHOT_DIGEST": digest,
           "TIME_LIMIT_S": "60"}
    print("exit code", main(env, s3))
    print("exit code", main({k: v for k, v in env.items() if k != "RESULT_BUCKET"}, s3))
