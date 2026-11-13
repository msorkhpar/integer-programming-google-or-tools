from plan_gate import gate

PROTECTED = {"aws_s3_bucket", "aws_ecr_repository", "aws_dynamodb_table_item"}


def change(address, kind, *actions, mode="managed"):
    return {"address": address, "mode": mode, "type": kind, "name": address.rsplit(".", 1)[-1],
            "change": {"actions": list(actions)}}


def plan(*changes):
    return {"format_version": "1.2", "resource_changes": list(changes)}


def test_a_plan_is_counted_and_a_protected_delete_blocked():
    p = plan(change("aws_s3_bucket.surveys", "aws_s3_bucket", "delete"),
             change("aws_batch_job_queue.trim", "aws_batch_job_queue", "update"),
             change("aws_iam_role.trim", "aws_iam_role", "create"),
             change("aws_ecr_repository.trim", "aws_ecr_repository", "no-op"))
    assert gate(p, PROTECTED) == (["aws_s3_bucket.surveys"],
                                  {"delete": 1, "update": 1, "create": 1, "no-op": 1})


def test_a_replacement_is_one_change_and_blocked_in_either_order():
    p = plan(change("aws_s3_bucket.a", "aws_s3_bucket", "delete", "create"),
             change("aws_s3_bucket.b", "aws_s3_bucket", "create", "delete"))
    assert gate(p, PROTECTED) == (["aws_s3_bucket.a", "aws_s3_bucket.b"], {"replace": 2})


def test_a_protected_resource_inside_a_module_is_still_protected():
    p = plan(change("module.storage.aws_s3_bucket.runs", "aws_s3_bucket", "delete"))
    assert gate(p, PROTECTED) == (["module.storage.aws_s3_bucket.runs"], {"delete": 1})


def test_an_allowed_address_may_be_deleted():
    p = plan(change("aws_s3_bucket.scratch", "aws_s3_bucket", "delete"),
             change("aws_s3_bucket.runs", "aws_s3_bucket", "delete"))
    assert gate(p, PROTECTED, allowed={"aws_s3_bucket.scratch"}) == (["aws_s3_bucket.runs"], {"delete": 2})


def test_unprotected_deletes_pass_and_data_reads_are_counted():
    p = plan(change("aws_lambda_function.old", "aws_lambda_function", "delete"),
             change("data.aws_caller_identity.current", "aws_caller_identity", "read", mode="data"))
    assert gate(p, PROTECTED) == ([], {"delete": 1, "read": 1})
