from __future__ import annotations

from collections import Counter  # noqa: F401

VERBS = {("no-op",): "no-op", ("create",): "create", ("read",): "read", ("update",): "update",
         ("delete",): "delete", ("delete", "create"): "replace", ("create", "delete"): "replace"}


def gate(plan: dict, protected: set[str], allowed: set[str] = frozenset()) -> tuple[list[str], dict[str, int]]:
    """(addresses blocked, sorted; count of changes by verb) for a `terraform show -json` plan."""
    # TODO: count each change's verb, and block deletes of protected types not in `allowed`.
    return [], {}
