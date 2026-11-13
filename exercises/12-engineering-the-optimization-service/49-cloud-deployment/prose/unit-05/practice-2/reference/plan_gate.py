from __future__ import annotations

from collections import Counter

VERBS = {("no-op",): "no-op", ("create",): "create", ("read",): "read", ("update",): "update",
         ("delete",): "delete", ("delete", "create"): "replace", ("create", "delete"): "replace"}


def gate(plan: dict, protected: set[str], allowed: set[str] = frozenset()) -> tuple[list[str], dict[str, int]]:
    """(addresses blocked, sorted; count of changes by verb) for a `terraform show -json` plan."""
    blocked, counts = [], Counter()
    for change in plan.get("resource_changes", []):
        actions = change["change"]["actions"]
        counts[VERBS[tuple(actions)]] += 1
        if change["type"] in protected and "delete" in actions and change["address"] not in allowed:
            blocked.append(change["address"])
    return sorted(blocked), dict(counts)
