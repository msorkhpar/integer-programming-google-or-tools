from __future__ import annotations

import re

#: Fargate's vCPU values and the memory (MiB) each allows, from the AWS Batch API reference.
FARGATE = {
    0.25: [512, 1024, 2048],
    0.5: list(range(1024, 4096 + 1, 1024)),
    1.0: list(range(2048, 8192 + 1, 1024)),
    2.0: list(range(4096, 16384 + 1, 1024)),
    4.0: list(range(8192, 30720 + 1, 1024)),
    8.0: list(range(16384, 61440 + 1, 4096)),
    16.0: list(range(32768, 122880 + 1, 8192)),
    32.0: [61440, 122880, 249856],
}
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,127}")


def problems(request: dict) -> list[str]:
    """Every rule of AWS Batch's SubmitJob that a Fargate request breaks, in the order checked."""
    found = []
    name = request.get("jobName", "")
    if not NAME.fullmatch(name):
        found.append(f"jobName {name!r} is not a valid job name")
    seconds = request.get("timeout", {}).get("attemptDurationSeconds")
    if seconds is not None and seconds < 60:
        found.append(f"timeout {seconds} s is under 60 s")
    attempts = request.get("retryStrategy", {}).get("attempts")
    if attempts is not None and not 1 <= attempts <= 10:
        found.append(f"retry attempts {attempts} is outside 1-10")
    overrides = request.get("containerOverrides", {})
    size = {r["type"]: r["value"] for r in overrides.get("resourceRequirements", [])}
    if ("VCPU" in size) != ("MEMORY" in size):
        found.append("VCPU and MEMORY must be given together")
    elif size and int(size["MEMORY"]) not in FARGATE.get(float(size["VCPU"]), []):
        found.append(f"VCPU {size['VCPU']} with MEMORY {size['MEMORY']} is not a Fargate size")
    seen = set()
    for variable in overrides.get("environment", []):
        if variable["name"] in seen:
            found.append(f"environment variable {variable['name']} is set twice")
        seen.add(variable["name"])
    return found
