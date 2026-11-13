"""Lesson 12.5.3: snapshots and results in S3, each written once under a key derived from its content.

The snapshot's key is its SHA-256 digest over the canonical form of lesson 12.2.3, so equal content
lands on one object. Every write is conditional (If-None-Match: *), so an object is never replaced,
and every read re-hashes the bytes before trusting them. GridCap is a fictional utility.
"""

from __future__ import annotations

import hashlib
import json

from botocore.exceptions import ClientError

from canonical import canonical
from snapshot import Snapshot


class Corrupted(Exception):
    """An object's bytes no longer hash to the digest in its key."""


def snapshot_key(digest: str) -> str:
    return f"snapshots/sha256/{digest}.json"


def result_key(digest: str, run_id: str) -> str:
    return f"results/{digest}/{run_id}.json"


def error_code(error: ClientError) -> str:
    return error.response["Error"]["Code"]


class S3Store:
    """Snapshots and results of the solve service, in one bucket."""

    def __init__(self, s3, bucket: str):
        self.s3 = s3
        self.bucket = bucket

    def _create(self, key: str, data: bytes) -> bool:
        """Write `data` at `key` unless an object is already there. True if this call wrote it."""
        try:
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, IfNoneMatch="*",
                               ContentType="application/json")
        except ClientError as error:
            if error_code(error) == "PreconditionFailed":
                return False
            raise
        return True

    def put_snapshot(self, snap: Snapshot) -> str:
        """Store a validated snapshot under its digest; return the digest. Equal content is stored once."""
        data = canonical(snap)
        digest = hashlib.sha256(data).hexdigest()
        self._create(snapshot_key(digest), data)
        return digest

    def get_snapshot(self, digest: str) -> Snapshot:
        """Read a snapshot, re-hash it, and validate it again; refuse an object that changed."""
        data = self.s3.get_object(Bucket=self.bucket, Key=snapshot_key(digest))["Body"].read()
        found = hashlib.sha256(data).hexdigest()
        if found != digest:
            raise Corrupted(f"snapshot {digest[:12]} now hashes to {found[:12]}")
        return Snapshot.model_validate_json(data)

    def put_result(self, digest: str, run_id: str, result: dict) -> str:
        """Write a run's result once. A second write for the same run is refused, not merged."""
        key = result_key(digest, run_id)
        body = json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8")
        if not self._create(key, body):
            raise FileExistsError(f"{key} already holds a result")
        return key

    def get_result(self, key: str) -> dict | None:
        """A finished run's result, or None while the object does not exist yet."""
        try:
            body = self.s3.get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except ClientError as error:
            if error_code(error) == "NoSuchKey":
                return None
            raise
        return json.loads(body)
