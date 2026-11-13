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
    found: list[str] = []
    # TODO: name, timeout, retries, size, environment, in that order.
    return found
