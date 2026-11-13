from __future__ import annotations

import re  # noqa: F401

#: (most circuits, vCPU, memory MiB): the smallest size whose bound covers the plan wins.
SIZES = [(500, 1, 2048), (5000, 2, 8192), (None, 4, 16384)]


def job_name(plan_id: str) -> str:
    """A name Batch accepts: letters, digits, hyphens, underscores; alphanumeric first; 128 at most."""
    return plan_id


def size_for(circuits: int) -> tuple[int, int]:
    # TODO: the first row of SIZES whose bound covers `circuits` (None covers everything).
    return 0, 0


def submit_trim(batch, queue: str, definition: str, plan_id: str, circuits: int, limit_s: int) -> str:
    """Submit one trim-planning solve; return Batch's job id."""
    # TODO: one batch.submit_job call with the name, the overrides and the timeout.
    return ""
