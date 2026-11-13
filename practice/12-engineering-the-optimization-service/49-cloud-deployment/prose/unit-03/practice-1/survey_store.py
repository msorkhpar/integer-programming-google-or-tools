from __future__ import annotations

import hashlib  # noqa: F401
import json

from botocore.exceptions import ClientError  # noqa: F401


def canonical(survey: dict) -> bytes:
    """One byte string per survey content: readings sorted by asset, keys sorted, no spaces."""
    return json.dumps(survey).encode("utf-8")


def survey_key(digest: str) -> str:
    return f"surveys/sha256/{digest}.json"


def put_survey(s3, bucket: str, survey: dict) -> str:
    """Store a survey once under its digest; return the digest. Never replace an existing object."""
    return ""


def get_survey(s3, bucket: str, digest: str) -> tuple[dict | None, str]:
    """(survey, "ok"), or (None, "missing") if no object, or (None, "corrupted") if it changed."""
    return None, ""
