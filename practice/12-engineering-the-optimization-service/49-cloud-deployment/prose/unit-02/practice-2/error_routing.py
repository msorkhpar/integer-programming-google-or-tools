from __future__ import annotations


def matches(names: list[str], error: str) -> bool:
    """Whether an ErrorEquals list names `error`, with the two wildcards."""
    return False


def route(state: dict, errors: list[str]) -> list[str]:
    """What the Task state does when its attempts fail with `errors`, in order, and the next one succeeds."""
    actions: list[str] = []
    # TODO: retriers first (the first matching one, within its MaxAttempts), then catchers, else fail.
    return actions
