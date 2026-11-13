from __future__ import annotations

import re


def matches(pattern: str, value: str, ignore_case: bool) -> bool:
    """IAM's wildcards: * is any run of characters, ? is one character; nothing else is special."""
    regex = "".join(".*" if c == "*" else "." if c == "?" else re.escape(c) for c in pattern)
    return re.fullmatch(regex, value, re.IGNORECASE if ignore_case else 0) is not None


def as_list(value) -> list[str]:
    return [value] if isinstance(value, str) else list(value)


def applies(statement: dict, action: str, resource: str) -> bool:
    return (any(matches(a, action, True) for a in as_list(statement["Action"]))
            and any(matches(r, resource, False) for r in as_list(statement["Resource"])))


def allowed(policy: dict, action: str, resource: str) -> bool:
    """Whether this one policy allows the request: an explicit Deny wins, then an Allow, else denied."""
    hits = [s["Effect"] for s in policy["Statement"] if applies(s, action, resource)]
    return "Allow" in hits and "Deny" not in hits
