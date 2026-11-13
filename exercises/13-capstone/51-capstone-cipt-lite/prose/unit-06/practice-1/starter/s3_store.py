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
    # TODO
    return b""


def from_json(data: bytes) -> dict:
    """The snapshot back from its bytes, every year key an integer again."""
    # TODO
    return {}


def put_snapshot(s3, bucket: str, snapshot: dict) -> str:
    """Store the snapshot under its digest, once; return the digest."""
    # TODO: head_object first; put_object only if nothing is stored under that key.
    return ""


def get_snapshot(s3, bucket: str, digest: str) -> dict:
    """The snapshot stored under `digest`, re-hashed before it is trusted."""
    # TODO
    return {}


if __name__ == "__main__":
    print(canonical({"years": [2027], "budget": {2027: 100}}).decode("ascii"))
