"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from plan_gate import gate


def change(address, kind, *actions):
    return {"address": address, "mode": "managed", "type": kind, "name": address.rsplit(".", 1)[-1],
            "change": {"actions": list(actions)}}


protected = {"aws_s3_bucket", "aws_dynamodb_table"}
plan = {"format_version": "1.2", "resource_changes": [
    change("aws_dynamodb_table.locks", "aws_dynamodb_table", "create", "delete"),
    change("aws_s3_bucket.archive", "aws_s3_bucket", "delete"),
    change("aws_s3_bucket.tmp", "aws_s3_bucket", "delete"),
    change("aws_lambda_function.solve", "aws_lambda_function", "update"),
    change("aws_sqs_queue.jobs", "aws_sqs_queue", "no-op"),
]}

print("plan, nothing allowed:", gate(plan, protected))
print("plan, aws_s3_bucket.tmp allowed:", gate(plan, protected, allowed={"aws_s3_bucket.tmp"}))
