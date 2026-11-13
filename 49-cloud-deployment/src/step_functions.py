"""Lesson 12.5.2: the run's state machine, read from its definition, and started twice under one name.

The definition is the read-along file deploy/stepfunctions/solve-run.asl.json. moto stores the state
machine and its executions but runs none of its states, so the program calls the failure function
itself with the input its Catch would pass. No AWS is reached. GridCap is fictional.
"""

import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

from fake_aws import fake_aws
from record_failure import handler
from s3_store import S3Store

DEFINITION = Path(__file__).resolve().parents[1] / "deploy" / "stepfunctions" / "solve-run.asl.json"
asl = json.loads(DEFINITION.read_text(encoding="utf-8"))

for name, state in asl["States"].items():
    service = state.get("Resource", "").removeprefix("arn:aws:states:::")
    on_error = [c["Next"] for c in state.get("Catch", [])]
    after = state.get("Next") or ("end: " + state["Type"])
    print(f"{name:<14} {state['Type']:<8} {service:<20} next {after:<14} on error {on_error or '-'}")

with fake_aws():
    sfn = boto3.client("stepfunctions")
    machine = sfn.create_state_machine(name="gridcap-solve-run", definition=DEFINITION.read_text(),
                                       roleArn="arn:aws:iam::123456789012:role/gridcap-solve-run")["stateMachineArn"]
    run = {"run_id": "run-0007", "snapshot_digest": "730c8b40b1eb" + "0" * 52, "time_limit_s": "60"}
    first = sfn.start_execution(stateMachineArn=machine, name=run["run_id"], input=json.dumps(run))
    again = sfn.start_execution(stateMachineArn=machine, name=run["run_id"], input=json.dumps(run))
    print("same name, same input -> same execution:", first["executionArn"] == again["executionArn"])
    try:
        sfn.start_execution(stateMachineArn=machine, name=run["run_id"],
                            input=json.dumps({**run, "time_limit_s": "120"}))
    except ClientError as error:
        print("same name, other input ->", error.response["Error"]["Code"])

    os.environ["RESULT_BUCKET"] = "gridcap-runs-example"
    s3 = boto3.client("s3")
    s3.create_bucket(Bucket="gridcap-runs-example")
    caught = {**run, "error": {"Error": "States.TaskFailed", "Cause": "OutOfMemoryError: Container killed"}}
    key = handler(caught, s3=s3)["result_key"]
    print("RecordFailure returned:", key.replace(run["snapshot_digest"], run["snapshot_digest"][:12] + "..."))
    print("a poll now finds:", S3Store(s3, "gridcap-runs-example").get_result(
        f"results/{run['snapshot_digest']}/run-0007.json")["status"])
    print("called again (a retry):", handler(caught, s3=s3))
