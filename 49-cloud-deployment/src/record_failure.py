"""Lesson 12.5.2: the Lambda function the state machine calls when the Batch job itself fails.

The worker writes a result for every way a solve ends, but a job that never ran it (the image
could not be pulled, the container ran out of memory, the job timed out) leaves no result. This
short function writes a `failed` result for such a run, so a poll always finds an answer. It is
called with the state's input plus the error Step Functions caught under "error".
"""

from __future__ import annotations

import os

from s3_store import S3Store


def handler(event: dict, context=None, s3=None) -> dict:
    """Lambda's entry point. `s3` is for tests; in AWS the client is made from the function's role."""
    if s3 is None:
        import boto3
        s3 = boto3.client("s3")
    store = S3Store(s3, os.environ["RESULT_BUCKET"])
    error = event.get("error", {})
    record = {"run_id": event["run_id"], "snapshot_digest": event["snapshot_digest"], "status": "failed",
              "message": f"the solve job failed before writing a result: {error.get('Error', 'unknown')}"}
    try:
        key = store.put_result(event["snapshot_digest"], event["run_id"], record)
    except FileExistsError:                       # the worker wrote a result after all; keep it
        key = None
    return {"run_id": event["run_id"], "result_key": key}
