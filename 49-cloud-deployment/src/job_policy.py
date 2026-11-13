"""Lesson 12.5.5: the solve job's IAM policy, read from the same file Terraform reads, and checked.

`allows` is a small model of IAM for this policy's shape only: Allow statements whose Action and
Resource patterns match (wildcards as IAM writes them). It knows no Deny, no conditions and no other
policy types, so it checks what this file says, not what AWS will decide. GridCap is fictional.
"""

import fnmatch
import json
from pathlib import Path
from string import Template

FILE = Path(__file__).resolve().parents[1] / "deploy" / "terraform" / "solve-job-policy.json"
BUCKET_ARN = "arn:aws:s3:::gridcap-runs-example"


def policy(bucket_arn: str) -> dict:
    """The policy document Terraform's templatefile() would render for this bucket."""
    return json.loads(Template(FILE.read_text(encoding="utf-8")).substitute(bucket_arn=bucket_arn))


def allows(doc: dict, action: str, resource: str) -> bool:
    return any(s["Effect"] == "Allow"
               and any(fnmatch.fnmatchcase(action.lower(), a.lower()) for a in s["Action"])
               and any(fnmatch.fnmatchcase(resource, r) for r in s["Resource"])
               for s in doc["Statement"])


if __name__ == "__main__":
    doc = policy(BUCKET_ARN)
    for sid in (s["Sid"] for s in doc["Statement"]):
        print("statement", sid)
    asks = [("s3:GetObject", "snapshots/sha256/730c8b40b1eb.json"),
            ("s3:PutObject", "results/730c8b40b1eb/run-0007.json"),
            ("s3:PutObject", "snapshots/sha256/730c8b40b1eb.json"),
            ("s3:DeleteObject", "results/730c8b40b1eb/run-0007.json"),
            ("s3:GetObject", "results/730c8b40b1eb/run-0006.json")]
    for action, key in asks:
        print(f"{action:<16} {key:<38} {'allowed' if allows(doc, action, f'{BUCKET_ARN}/{key}') else 'denied'}")
