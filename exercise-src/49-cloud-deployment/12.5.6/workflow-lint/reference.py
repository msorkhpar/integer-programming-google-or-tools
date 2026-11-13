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
    found = set()
    top = workflow.get("permissions")
    if top is None:
        found.add("workflow: no top-level permissions")
    elif top == "write-all":
        found.add("workflow: permissions write-all")
    for name, job in workflow.get("jobs", {}).items():
        perms = job.get("permissions", {})
        if perms == "write-all":
            found.add(f"{name}: permissions write-all")
        steps = job.get("steps", [])
        uses = [step["uses"] for step in steps if "uses" in step]
        for ref in uses:
            if not ref.startswith("./") and not PINNED.fullmatch(ref):
                found.add(f"{name}: {ref} is not pinned to a commit SHA")
        for secret in SECRET.findall(" ".join(texts(steps))):
            if secret != "GITHUB_TOKEN":
                found.add(f"{name}: uses secret {secret}")
        granted = job.get("permissions", top)            # a job with no permissions of its own gets the workflow's
        if isinstance(granted, dict) and granted.get("id-token") == "write" and not any(u.startswith(AWS_STEP) for u in uses):
            found.add(f"{name}: id-token: write without an AWS credentials step")
    return sorted(found)
