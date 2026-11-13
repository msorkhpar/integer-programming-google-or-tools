import os

import boto3
import pytest
from moto import mock_aws

from trim_jobs import submit_trim

for name in ("AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN"):
    os.environ[name] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def batch():
    with mock_aws(config={"batch": {"use_docker": False}}):
        ec2, iam, client = boto3.client("ec2"), boto3.client("iam"), boto3.client("batch")
        vpc = ec2.create_vpc(CidrBlock="10.9.0.0/16")["Vpc"]["VpcId"]
        subnet = ec2.create_subnet(VpcId=vpc, CidrBlock="10.9.1.0/24")["Subnet"]["SubnetId"]
        group = ec2.create_security_group(GroupName="trim", Description="trim", VpcId=vpc)["GroupId"]
        role = iam.create_role(RoleName="trim", AssumeRolePolicyDocument="{}")["Role"]["Arn"]
        env = client.create_compute_environment(
            computeEnvironmentName="trim-fargate", type="MANAGED", state="ENABLED", serviceRole=role,
            computeResources={"type": "FARGATE", "maxvCpus": 8, "subnets": [subnet], "securityGroupIds": [group]},
        )["computeEnvironmentArn"]
        client.create_job_queue(jobQueueName="trim-queue", state="ENABLED", priority=1,
                                computeEnvironmentOrder=[{"order": 1, "computeEnvironment": env}])
        client.register_job_definition(
            jobDefinitionName="trim-solve", type="container", platformCapabilities=["FARGATE"],
            containerProperties={"image": "trim:1", "executionRoleArn": role,
                                 "resourceRequirements": [{"type": "VCPU", "value": "1"},
                                                          {"type": "MEMORY", "value": "2048"}]})
        sent = []
        client.meta.events.register("provide-client-params.batch.SubmitJob",
                                    lambda params, **kwargs: sent.append(params))
        client.sent = sent
        yield client


def submitted(batch, plan_id="2031-west", circuits=120, limit_s=300):
    job_id = submit_trim(batch, "trim-queue", "trim-solve", plan_id, circuits, limit_s)
    assert len(batch.sent) == 1, "submit_trim must call submit_job exactly once"
    params = batch.sent[0]
    overrides = params.get("containerOverrides", {})
    env = {e["name"]: e["value"] for e in overrides.get("environment", [])}
    size = {r["type"]: r["value"] for r in overrides.get("resourceRequirements", [])}
    return job_id, params, env, size


def test_a_small_plan_is_submitted_with_its_settings(batch):
    job_id, params, env, size = submitted(batch)
    assert params["jobName"] == "2031-west" and params["jobQueue"] == "trim-queue"
    assert params["jobDefinition"] == "trim-solve"
    assert env == {"PLAN_ID": "2031-west", "TIME_LIMIT_S": "300", "CPSAT_WORKERS": "1"}
    assert size == {"VCPU": "1", "MEMORY": "2048"}
    assert params["timeout"] == {"attemptDurationSeconds": 600}
    assert batch.describe_jobs(jobs=[job_id])["jobs"][0]["jobName"] == "2031-west"


def test_sizes_follow_the_circuit_count_at_the_bounds(batch):
    sizes = []
    for circuits in (500, 5000, 5001):
        batch.sent.clear()
        sizes.append(submitted(batch, circuits=circuits)[3])
    assert sizes == [{"VCPU": "1", "MEMORY": "2048"}, {"VCPU": "2", "MEMORY": "8192"},
                     {"VCPU": "4", "MEMORY": "16384"}]


def test_the_solver_gets_one_worker_per_vcpu(batch):
    _, _, env, size = submitted(batch, circuits=9000)
    assert env.get("CPSAT_WORKERS") == size.get("VCPU") == "4"


def test_a_short_limit_still_gets_the_60_second_minimum(batch):
    _, params, _, _ = submitted(batch, limit_s=20)
    assert params.get("timeout") == {"attemptDurationSeconds": 60}


def test_a_plan_id_becomes_a_valid_job_name(batch):
    _, params, env, _ = submitted(batch, plan_id="#7 west/north")
    assert params.get("jobName") == "7-west-north" and env.get("PLAN_ID") == "#7 west/north"


def test_a_long_plan_id_is_cut_to_128_characters(batch):
    _, params, _, _ = submitted(batch, plan_id="p" * 200)
    assert params.get("jobName") == "p" * 128
