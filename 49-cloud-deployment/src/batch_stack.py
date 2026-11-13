"""Lesson 12.5.2: the Batch side of the stack, created in moto the way Terraform creates it in AWS.

A Fargate compute environment, one job queue, and the solve job definition. The account id is
moto's placeholder, 123456789012; the image name is an example. GridCap is a fictional utility.
"""

from __future__ import annotations

from dataclasses import dataclass

IMAGE = "123456789012.dkr.ecr.us-east-1.amazonaws.com/gridcap-solver:2026.11.1"


@dataclass(frozen=True)
class Stack:
    queue: str
    definition: str


def job_definition(execution_role: str, job_role: str) -> dict:
    """The solve job's definition: the image, its command, its size, its timeout and its retries."""
    return dict(
        jobDefinitionName="gridcap-solve",
        type="container",
        platformCapabilities=["FARGATE"],
        containerProperties={
            "image": IMAGE,
            "command": ["python", "-c", "import solve_worker; raise SystemExit(solve_worker.main())"],
            "executionRoleArn": execution_role,      # lets Fargate pull the image and write logs
            "jobRoleArn": job_role,                  # what the solve itself may do in S3
            "resourceRequirements": [{"type": "VCPU", "value": "2"}, {"type": "MEMORY", "value": "8192"}],
            "environment": [{"name": "RESULT_BUCKET", "value": "gridcap-runs-example"},
                            {"name": "PYTHON_CPU_COUNT", "value": "2"}],
            "networkConfiguration": {"assignPublicIp": "DISABLED"},
        },
        timeout={"attemptDurationSeconds": 3600},
        retryStrategy={"attempts": 2},
    )


def create_stack(ec2, iam, batch) -> Stack:
    vpc = ec2.create_vpc(CidrBlock="10.20.0.0/16")["Vpc"]["VpcId"]
    subnet = ec2.create_subnet(VpcId=vpc, CidrBlock="10.20.1.0/24")["Subnet"]["SubnetId"]
    group = ec2.create_security_group(GroupName="gridcap-solve", Description="solve jobs", VpcId=vpc)["GroupId"]
    role = {name: iam.create_role(RoleName=name, AssumeRolePolicyDocument="{}")["Role"]["Arn"]
            for name in ("gridcap-batch-service", "gridcap-solve-execution", "gridcap-solve-job")}
    env = batch.create_compute_environment(
        computeEnvironmentName="gridcap-fargate", type="MANAGED", state="ENABLED",
        computeResources={"type": "FARGATE", "maxvCpus": 16, "subnets": [subnet], "securityGroupIds": [group]},
        serviceRole=role["gridcap-batch-service"])["computeEnvironmentArn"]
    batch.create_job_queue(jobQueueName="gridcap-solves", state="ENABLED", priority=1,
                           computeEnvironmentOrder=[{"order": 1, "computeEnvironment": env}])
    batch.register_job_definition(**job_definition(role["gridcap-solve-execution"], role["gridcap-solve-job"]))
    return Stack(queue="gridcap-solves", definition="gridcap-solve")
