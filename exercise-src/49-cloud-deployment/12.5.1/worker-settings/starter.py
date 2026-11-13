from __future__ import annotations

from typing import Mapping

CREDENTIAL_WORDS = ("SECRET", "PASSWORD", "ACCESS_KEY")


def whole(text: str, name: str, low: int, high: int, problems: list[str]) -> int | None:
    """`text` as a whole number in [low, high], or None with a problem added."""
    # TODO: parse the number; add "NAME='text' is not a whole number" or "NAME value is outside low-high".
    return None


def read_settings(env: Mapping[str, str]) -> tuple[dict | None, list[str]]:
    """The roster worker's settings from its environment, or None and every problem found."""
    problems: list[str] = []
    # TODO: check every variable, collect every problem, and only then decide.
    return {}, problems
