"""Lesson 12.5.4: what moto checks like AWS does, and what it accepts that AWS would not.

Every call goes to moto's fake (no AWS is reached). GridCap is a fictional utility.
"""

import base64
import hashlib
import json
import time

import boto3
from botocore.exceptions import ClientError

from batch_stack import create_stack
from fake_aws import fake_aws

BUCKET = "gridcap-runs-example"

with fake_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=BUCKET)
    for i in range(1005):
        s3.put_object(Bucket=BUCKET, Key=f"results/run-{i:04d}.json", Body=b"{}")
    one = s3.list_objects_v2(Bucket=BUCKET, Prefix="results/")
    print("one list call:", one["KeyCount"], "keys, IsTruncated", one["IsTruncated"])
    pages = s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix="results/")
    print("paginator:", sum(len(p.get("Contents", [])) for p in pages), "keys")

    try:
        s3.get_object(Bucket=BUCKET, Key="results/run-9999.json")
    except ClientError as error:
        print("missing key:", error.response["Error"]["Code"])
    try:
        s3.get_object(Bucket="gridcap-no-such-bucket", Key="results/run-0001.json")
    except ClientError as error:
        print("missing bucket:", error.response["Error"]["Code"])

    wrong = base64.b64encode(hashlib.sha256(b"other bytes").digest()).decode()
    s3.put_object(Bucket=BUCKET, Key="snapshots/check.json", Body=b"{}", ChecksumSHA256=wrong)
    print("upload with a wrong SHA-256 checksum: accepted")

    sfn = boto3.client("stepfunctions")
    sfn.create_state_machine(name="broken", roleArn="arn:aws:iam::123456789012:role/sfn",
                             definition=json.dumps({"StartAt": "Solve", "States": {}}))
    print("state machine whose StartAt names no state: accepted")

    batch = boto3.client("batch")
    stack = create_stack(boto3.client("ec2"), boto3.client("iam"), batch)
    job = batch.submit_job(jobName="run-0001", jobQueue=stack.queue, jobDefinition=stack.definition)
    status = "SUBMITTED"
    while status not in ("SUCCEEDED", "FAILED"):
        time.sleep(0.1)
        status = batch.describe_jobs(jobs=[job["jobId"]])["jobs"][0]["status"]
    print("Batch job submitted without RUN_ID or SNAPSHOT_DIGEST:", status)
    odd = batch.submit_job(jobName="run 0002!", jobQueue=stack.queue, jobDefinition=stack.definition,
                           timeout={"attemptDurationSeconds": 30})
    print("job name 'run 0002!' with a 30 s timeout: accepted,", batch.describe_jobs(
        jobs=[odd["jobId"]])["jobs"][0]["timeout"])
