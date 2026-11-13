"""Lesson 12.5.4: why the fake credentials come first. A client with none cannot sign a request.

The child process stands for a test run on a machine with no AWS credentials and no network: its
environment has no AWS variables and points boto3 at no config file. GridCap is a fictional utility.
"""

import os
import subprocess
import sys

import boto3

from fake_aws import FAKE_CREDENTIALS, fake_aws

CALL = """
import boto3
try:
    boto3.client("s3", region_name="us-east-1").list_buckets()
except Exception as error:
    print(type(error).__name__ + ":", error)
"""
bare = {k: v for k, v in os.environ.items() if not k.startswith("AWS_")}
bare |= {"AWS_CONFIG_FILE": os.devnull, "AWS_SHARED_CREDENTIALS_FILE": os.devnull, "AWS_EC2_METADATA_DISABLED": "true"}
print("no credentials, no mock:", subprocess.run([sys.executable, "-c", CALL], env=bare, capture_output=True,
                                                 text=True).stdout.strip())

with fake_aws():
    print("fake credentials:", sorted(FAKE_CREDENTIALS))
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="gridcap-runs-example")
    print("inside the mock:", [b["Name"] for b in s3.list_buckets()["Buckets"]])
    print("account moto reports:", boto3.client("sts").get_caller_identity()["Account"])
