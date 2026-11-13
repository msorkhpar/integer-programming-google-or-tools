from __future__ import annotations

import re  # noqa: F401


def matches(pattern: str, value: str, ignore_case: bool) -> bool:
    """IAM's wildcards: * is any run of characters, ? is one character; nothing else is special."""
    return False


def as_list(value) -> list[str]:
    return list(value)


def applies(statement: dict, action: str, resource: str) -> bool:
    return False


def allowed(policy: dict, action: str, resource: str) -> bool:
    """Whether this one policy allows the request: an explicit Deny wins, then an Allow, else denied."""
    # TODO: collect the effects of the statements that apply; an explicit Deny wins.
    return False
