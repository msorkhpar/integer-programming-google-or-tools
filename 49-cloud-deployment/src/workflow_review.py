"""Lesson 12.5.6: read the CI workflow as data. Which jobs run for each event, and what each may do.

The workflow is the read-along file deploy/github-workflows/ci.yml. This program parses it with
PyYAML and reasons about it; it runs nothing on GitHub. GridCap is a fictional utility.
"""

import re
from pathlib import Path

import yaml

FILE = Path(__file__).resolve().parents[1] / "deploy" / "github-workflows" / "ci.yml"
flow = yaml.safe_load(FILE.read_text(encoding="utf-8"))
print("top-level keys:", list(flow))                   # YAML 1.1 reads the bare key `on` as True

jobs = flow["jobs"]


def needs(job: dict) -> list[str]:
    n = job.get("needs", [])
    return [n] if isinstance(n, str) else n


def runs_on(event: str) -> dict[str, str]:
    """Each job's fate for one event: an `if` on the event name, then skipped if any need did not run."""
    fate: dict[str, str] = {}
    for name, job in jobs.items():                       # the file lists every job after its needs
        condition = job.get("if", "")
        wanted = re.search(r"github\.event_name == '(\w+)'", condition)
        if any(fate[n] != "runs" for n in needs(job)) or (wanted and wanted.group(1) != event):
            fate[name] = "skipped"
        else:
            fate[name] = "runs"
    return fate


for event in ("pull_request", "push"):
    print(f"{event:<13}", runs_on(event))

for name, job in jobs.items():
    pins = [step["uses"] for step in job["steps"] if "uses" in step]
    pinned = all(re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", u) for u in pins)
    perms = job.get("permissions", flow["permissions"])
    print(f"{name:<7} needs {needs(job) or '-'!s:<17} permissions {perms}, every action SHA-pinned: {pinned}, "
          f"environment: {job.get('environment', '-')}")
print("secrets referenced:", sorted(set(re.findall(r"secrets\.\w+", FILE.read_text(encoding="utf-8")))))
