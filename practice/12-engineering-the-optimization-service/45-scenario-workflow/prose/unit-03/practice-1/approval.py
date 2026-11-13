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
    # TODO
    return []


def walk(state: str, actions: list[str]) -> tuple[str, str | None]:
    """Apply the actions in order; stop at the first refused one. (final state, refused action or None)."""
    # TODO
    return state, None


def reachable(state: str) -> list[str]:
    """Every state some sequence of allowed actions can lead to from `state`, itself included, sorted."""
    # TODO
    return []


if __name__ == "__main__":
    print(walk("Draft", ["edit", "submit", "approve"]), reachable("Approved"))
