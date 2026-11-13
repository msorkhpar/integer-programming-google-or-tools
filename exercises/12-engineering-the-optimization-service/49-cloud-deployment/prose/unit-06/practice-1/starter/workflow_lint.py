from __future__ import annotations

import re

PINNED = re.compile(r"[^@\s]+@[0-9a-f]{40}")
SECRET = re.compile(r"secrets\.(\w+)")
AWS_STEP = "aws-actions/configure-aws-credentials@"


def texts(value) -> list[str]:
    """Every string inside a YAML value: a step's run, its with and env values."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [t for v in value.values() for t in texts(v)]
    if isinstance(value, list):
        return [t for v in value for t in texts(v)]
    return []


def lint(workflow: dict) -> list[str]:
    """The findings for a parsed workflow, sorted, each once."""
    found: set[str] = set()
    # TODO: the workflow's permissions, then each job's permissions, pins, secrets and id-token.
    return sorted(found)
