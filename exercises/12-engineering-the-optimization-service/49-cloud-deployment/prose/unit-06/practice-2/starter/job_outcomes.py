from __future__ import annotations

import re

EVENT = re.compile(r"github\.event_name == '(\w+)'")


def needs_of(job: dict) -> list[str]:
    needs = job.get("needs", [])
    return [needs] if isinstance(needs, str) else list(needs)


def outcomes(jobs: dict[str, dict], event: str, failing: set[str] = frozenset()) -> dict[str, str]:
    """Each job's outcome for one event: "success", "failure" or "skipped". Jobs in `failing` fail if they run."""
    # TODO: decide each job after the jobs it needs, whatever order the dict lists them in.
    return {name: "success" for name in jobs}
