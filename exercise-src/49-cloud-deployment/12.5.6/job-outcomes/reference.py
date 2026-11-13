from __future__ import annotations

import re

EVENT = re.compile(r"github\.event_name == '(\w+)'")


def needs_of(job: dict) -> list[str]:
    needs = job.get("needs", [])
    return [needs] if isinstance(needs, str) else list(needs)


def outcomes(jobs: dict[str, dict], event: str, failing: set[str] = frozenset()) -> dict[str, str]:
    """Each job's outcome for one event: "success", "failure" or "skipped". Jobs in `failing` fail if they run."""
    result: dict[str, str] = {}

    def decide(name: str) -> str:
        if name not in result:
            job = jobs[name]
            before = [decide(n) for n in needs_of(job)]
            condition = job.get("if", "")
            wanted = EVENT.search(condition)
            if wanted and wanted.group(1) != event:
                result[name] = "skipped"
            elif "always()" not in condition and any(o != "success" for o in before):
                result[name] = "skipped"
            else:
                result[name] = "failure" if name in failing else "success"
        return result[name]

    for name in jobs:
        decide(name)
    return result
