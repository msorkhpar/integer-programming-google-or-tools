"""Lesson 12.5.3: snapshots in S3 under their digest, written once, and checked again on every read.

S3 is moto's fake (no AWS is reached). The bucket has versioning on, as the Terraform of lesson
12.5.5 sets it. GridCap is a fictional utility.
"""

import copy
import hashlib
import json

import boto3
from botocore.exceptions import ClientError

from fake_aws import fake_aws
from gridcap import generate
from s3_store import Corrupted, S3Store, snapshot_key
from snapshot import export, load

BUCKET = "gridcap-runs-example"
doc = export(generate("small"))

with fake_aws():
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket=BUCKET)
    s3.put_bucket_versioning(Bucket=BUCKET, VersioningConfiguration={"Status": "Enabled"})
    store = S3Store(s3, BUCKET)

    first = store.put_snapshot(load(json.dumps(doc)))
    again = store.put_snapshot(load(json.dumps(doc, indent=2)))         # the same export, pretty-printed
    keys = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]]
    print("digest:", first[:12], "| re-sent export, same digest:", again == first, "| objects:", keys)

    try:
        s3.put_object(Bucket=BUCKET, Key=snapshot_key(first), Body=b"{}", IfNoneMatch="*")
    except ClientError as error:
        print("conditional overwrite:", error.response["Error"]["Code"],
              error.response["ResponseMetadata"]["HTTPStatusCode"])

    cut = copy.deepcopy(doc)
    cut["budget"][2]["amount"] = 7000                                  # finance cuts 2029
    second = store.put_snapshot(load(json.dumps(cut)))
    print("lean 2029: new digest", second[:12], "| objects:", s3.list_objects_v2(Bucket=BUCKET)["KeyCount"])

    print("result written:", store.put_result(first, "run-0007", {"run_id": "run-0007", "status": "optimal"}))
    try:
        store.put_result(first, "run-0007", {"run_id": "run-0007", "status": "failed"})
    except FileExistsError as error:
        print("second result for run-0007 refused:", error)

    edited = s3.get_object(Bucket=BUCKET, Key=snapshot_key(second))["Body"].read().replace(b'"amount":7000', b'"amount":7900')
    s3.put_object(Bucket=BUCKET, Key=snapshot_key(second), Body=edited)  # an unconditional overwrite
    try:
        store.get_snapshot(second)
    except Corrupted as error:
        print("read after an overwrite: refused,", error)
    versions = s3.list_object_versions(Bucket=BUCKET, Prefix=snapshot_key(second))["Versions"]
    earlier = next(v for v in versions if not v["IsLatest"])
    body = s3.get_object(Bucket=BUCKET, Key=snapshot_key(second), VersionId=earlier["VersionId"])["Body"].read()
    print("versions kept:", len(versions), "| the earlier one re-hashes to its key:",
          hashlib.sha256(body).hexdigest() == second)
