from __future__ import annotations

#: The board's workflow: (state, action) -> next state. A pair that is not here is refused.
TABLE = {
    ("Draft", "edit"): "Draft",
    ("Draft", "submit"): "Submitted",
    ("Submitted", "reject"): "Draft",
    ("Submitted", "approve"): "Approved",
    ("Approved", "archive"): "Archived",
}


def allowed(state: str) -> list[str]:
    """Every action `state` accepts, sorted."""
    return sorted(action for (s, action) in TABLE if s == state)


def walk(state: str, actions: list[str]) -> tuple[str, str | None]:
    """Apply the actions in order; stop at the first refused one. (final state, refused action or None)."""
    for action in actions:
        nxt = TABLE.get((state, action))
        if nxt is None:
            return state, action
        state = nxt
    return state, None


def reachable(state: str) -> list[str]:
    """Every state some sequence of allowed actions can lead to from `state`, itself included, sorted."""
    seen, todo = {state}, [state]
    while todo:
        here = todo.pop()
        for (s, _), nxt in TABLE.items():
            if s == here and nxt not in seen:
                seen.add(nxt)
                todo.append(nxt)
    return sorted(seen)


if __name__ == "__main__":
    print(walk("Draft", ["edit", "submit", "approve"]), reachable("Approved"))
