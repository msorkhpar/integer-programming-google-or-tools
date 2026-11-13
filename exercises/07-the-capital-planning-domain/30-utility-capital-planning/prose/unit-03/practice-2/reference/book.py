from __future__ import annotations

from copy import deepcopy

# A book maps each scenario name to {"stage", "inputs", "plan", "parent"}.


def create(book: dict, name: str, inputs: dict) -> bool:
    if name in book:
        return False
    book[name] = {"stage": "Initial", "inputs": deepcopy(inputs), "plan": None, "parent": None}
    return True


def checked(book: dict, name: str) -> bool:
    """The data checks passed: Initial moves to Pre-Opt."""
    if book[name]["stage"] != "Initial":
        return False
    book[name]["stage"] = "Pre-Opt"
    return True


def edit(book: dict, name: str, changes: dict) -> bool:
    s = book[name]
    if s["stage"] == "Budget Lock":
        return False
    s["inputs"].update(deepcopy(changes))
    if s["stage"] == "Post-Opt":
        s["stage"], s["plan"] = "Pre-Opt", None
    return True


def optimized(book: dict, name: str, plan: dict) -> bool:
    s = book[name]
    if s["stage"] != "Pre-Opt":
        return False
    s["stage"], s["plan"] = "Post-Opt", dict(plan)
    return True


def lock(book: dict, name: str) -> bool:
    if book[name]["stage"] != "Post-Opt" or any(s["stage"] == "Budget Lock" for s in book.values()):
        return False
    book[name]["stage"] = "Budget Lock"
    return True


def copy(book: dict, source: str, name: str) -> bool:
    if name in book:
        return False
    book[name] = {"stage": "Initial", "inputs": deepcopy(book[source]["inputs"]), "plan": None, "parent": source}
    return True


if __name__ == "__main__":
    book = {}
    print(create(book, "base", {"budget": 900}), checked(book, "base"), optimized(book, "base", {"W1": 2027}))
    print(lock(book, "base"), edit(book, "base", {"budget": 800}), book["base"]["stage"])
