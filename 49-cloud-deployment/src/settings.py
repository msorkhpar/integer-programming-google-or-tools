"""Lesson 12.5.1: the solve worker's settings, read from environment variables when the container starts.

The image is the same in every environment; what changes between a test run, staging and
production is the environment the container is started with. So the worker reads its settings
from variables, checks all of them at once, and refuses to start on any problem.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Mapping

DIGEST = re.compile(r"^[0-9a-f]{64}$")


class BadSettings(ValueError):
    """The container was started with settings the worker cannot run with."""


@dataclass(frozen=True)
class Settings:
    bucket: str             # RESULT_BUCKET: where snapshots are read and results written
    run_id: str             # RUN_ID: the run this container solves
    snapshot_digest: str    # SNAPSHOT_DIGEST: the snapshot to solve, by its SHA-256 digest
    time_limit_s: float     # TIME_LIMIT_S: the solver's time limit, 600 s unless set

    @classmethod
    def from_env(cls, env: Mapping[str, str]) -> "Settings":
        problems = [f"{name} is not set" for name in ("RESULT_BUCKET", "RUN_ID", "SNAPSHOT_DIGEST")
                    if not env.get(name)]
        digest = env.get("SNAPSHOT_DIGEST", "")
        if digest and not DIGEST.match(digest):
            problems.append("SNAPSHOT_DIGEST is not 64 lowercase hex characters")
        limit = number(env.get("TIME_LIMIT_S", "600"), float, "TIME_LIMIT_S", problems)
        if problems:
            raise BadSettings("; ".join(problems))
        return cls(env["RESULT_BUCKET"], env["RUN_ID"], digest, limit)


def number(text: str, kind, name: str, problems: list[str]):
    """`text` as a positive number of type `kind`, or a problem added to the list."""
    try:
        value = kind(text)
    except ValueError:
        problems.append(f"{name}={text!r} is not a number")
        return None
    if not math.isfinite(value) or value <= 0:
        problems.append(f"{name} must be a finite number above 0")
    return value
