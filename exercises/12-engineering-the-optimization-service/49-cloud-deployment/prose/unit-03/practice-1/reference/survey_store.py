from __future__ import annotations

import hashlib
import json

from botocore.exceptions import ClientError


def canonical(survey: dict) -> bytes:
    """One byte string per survey content: readings sorted by asset, keys sorted, no spaces."""
    readings = sorted(survey["readings"], key=lambda r: r["asset_id"])
    text = json.dumps({**survey, "readings": readings}, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return text.encode("ascii")


def survey_key(digest: str) -> str:
    return f"surveys/sha256/{digest}.json"


def put_survey(s3, bucket: str, survey: dict) -> str:
    """Store a survey once under its digest; return the digest. Never replace an existing object."""
    body = canonical(survey)
    digest = hashlib.sha256(body).hexdigest()
    try:
        s3.put_object(Bucket=bucket, Key=survey_key(digest), Body=body, IfNoneMatch="*")
    except ClientError as error:
        if error.response["Error"]["Code"] != "PreconditionFailed":
            raise
    return digest


def get_survey(s3, bucket: str, digest: str) -> tuple[dict | None, str]:
    """(survey, "ok"), or (None, "missing") if no object, or (None, "corrupted") if it changed."""
    try:
        found = s3.get_object(Bucket=bucket, Key=survey_key(digest))
    except s3.exceptions.NoSuchKey:
        return None, "missing"
    body = found["Body"].read()
    if hashlib.sha256(body).hexdigest() != digest:
        return None, "corrupted"
    return json.loads(body), "ok"
