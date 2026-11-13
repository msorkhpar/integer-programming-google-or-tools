from __future__ import annotations

import re

#: (most circuits, vCPU, memory MiB): the smallest size whose bound covers the plan wins.
SIZES = [(500, 1, 2048), (5000, 2, 8192), (None, 4, 16384)]


def job_name(plan_id: str) -> str:
    """A name Batch accepts: letters, digits, hyphens, underscores; alphanumeric first; 128 at most."""
    name = re.sub(r"[^A-Za-z0-9_-]", "-", plan_id).lstrip("-_") or "trim"
    return name[:128]


def size_for(circuits: int) -> tuple[int, int]:
    for most, vcpu, memory in SIZES:
        if most is None or circuits <= most:
            return vcpu, memory
    raise AssertionError("unreachable")


def submit_trim(batch, queue: str, definition: str, plan_id: str, circuits: int, limit_s: int) -> str:
    """Submit one trim-planning solve; return Batch's job id."""
    vcpu, memory = size_for(circuits)
    job = batch.submit_job(
        jobName=job_name(plan_id),
        jobQueue=queue,
        jobDefinition=definition,
        containerOverrides={
            "environment": [
                {"name": "PLAN_ID", "value": plan_id},
                {"name": "TIME_LIMIT_S", "value": str(limit_s)},
                {"name": "CPSAT_WORKERS", "value": str(vcpu)},
            ],
            "resourceRequirements": [
                {"type": "VCPU", "value": str(vcpu)},
                {"type": "MEMORY", "value": str(memory)},
            ],
        },
        timeout={"attemptDurationSeconds": max(60, 2 * limit_s)},
    )
    return job["jobId"]
