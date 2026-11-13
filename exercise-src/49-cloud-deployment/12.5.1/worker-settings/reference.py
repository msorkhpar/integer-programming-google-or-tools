from __future__ import annotations

from typing import Mapping

CREDENTIAL_WORDS = ("SECRET", "PASSWORD", "ACCESS_KEY")


def whole(text: str, name: str, low: int, high: int, problems: list[str]) -> int | None:
    """`text` as a whole number in [low, high], or None with a problem added."""
    try:
        value = int(text)
    except ValueError:
        problems.append(f"{name}={text!r} is not a whole number")
        return None
    if not low <= value <= high:
        problems.append(f"{name} {value} is outside {low}-{high}")
        return None
    return value


def read_settings(env: Mapping[str, str]) -> tuple[dict | None, list[str]]:
    """The roster worker's settings from its environment, or None and every problem found."""
    problems: list[str] = []
    bucket = env.get("ROSTER_BUCKET", "")
    if not bucket:
        problems.append("ROSTER_BUCKET is not set")
    season = None
    if not env.get("SEASON"):
        problems.append("SEASON is not set")
    else:
        season = whole(env["SEASON"], "SEASON", 2025, 2040, problems)
    crews = whole(env.get("CREWS", "4"), "CREWS", 1, 50, problems)
    dry = env.get("DRY_RUN", "false").lower()
    if dry not in ("true", "false"):
        problems.append(f"DRY_RUN={env['DRY_RUN']!r} is not true or false")
    for name in sorted(env):
        if any(word in name for word in CREDENTIAL_WORDS):
            problems.append(f"{name} must not be set: use the job role")
    if problems:
        return None, problems
    return {"bucket": bucket, "season": season, "crews": crews, "dry_run": dry == "true"}, []
