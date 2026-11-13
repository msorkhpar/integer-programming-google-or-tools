"""Milestone 6: a content-addressed snapshot store in S3.

Each snapshot is stored once, as `snapshots/<sha256>.json`, and checked again on every read. A
snapshot is a dict in the milestones' shape; its year keys are integers in Python and strings in
JSON. The practice portfolio is invented for a fictional utility.
"""

from __future__ import annotations

import hashlib
import json

from botocore.exceptions import ClientError


class Corrupted(Exception):
    """A stored object no longer hashes to the digest in its name."""


class NotStored(Exception):
    """No snapshot is stored under this digest."""


def canonical(snapshot: dict) -> bytes:
    """The snapshot as bytes: sorted keys, no spaces, ASCII only. JSON writes the year keys as text."""
    return json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def by_year(table: dict) -> dict:
    return {int(year): amount for year, amount in table.items()}


def from_json(data: bytes) -> dict:
    """The snapshot back from its bytes, every year key an integer again."""
    snap = json.loads(data)
    snap["budget"] = by_year(snap["budget"])
    snap["region_budget"] = {r: by_year(t) for r, t in snap["region_budget"].items()}
    snap["crews"] = {p: by_year(t) for p, t in snap["crews"].items()}
    for job in snap["projects"].values():
        job["npv"] = by_year(job["npv"])
    return snap


def key_of(digest: str) -> str:
    return f"snapshots/{digest}.json"


def stored(s3, bucket: str, digest: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key_of(digest))
        return True
    except ClientError as error:
        if error.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def put_snapshot(s3, bucket: str, snapshot: dict) -> str:
    """Store the snapshot under its digest, once; return the digest."""
    data = canonical(snapshot)
    digest = hashlib.sha256(data).hexdigest()
    if not stored(s3, bucket, digest):
        s3.put_object(Bucket=bucket, Key=key_of(digest), Body=data, ContentType="application/json")
    return digest


def get_snapshot(s3, bucket: str, digest: str) -> dict:
    """The snapshot stored under `digest`, re-hashed before it is trusted."""
    if not stored(s3, bucket, digest):
        raise NotStored(digest)
    data = s3.get_object(Bucket=bucket, Key=key_of(digest))["Body"].read()
    if hashlib.sha256(data).hexdigest() != digest:
        raise Corrupted(f"{key_of(digest)} no longer hashes to its name")
    return from_json(data)


if __name__ == "__main__":
    print(canonical({"years": [2027], "budget": {2027: 100}}).decode("ascii"))
