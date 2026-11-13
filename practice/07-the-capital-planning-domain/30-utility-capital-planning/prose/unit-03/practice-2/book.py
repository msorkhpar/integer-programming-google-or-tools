from __future__ import annotations

from copy import deepcopy

# A book maps each scenario name to {"stage", "inputs", "plan", "parent"}.
# TODO: every function below refuses everything and changes nothing; make each one keep the rules.


def create(book: dict, name: str, inputs: dict) -> bool:
    return False


def checked(book: dict, name: str) -> bool:
    """The data checks passed: Initial moves to Pre-Opt."""
    return False


def edit(book: dict, name: str, changes: dict) -> bool:
    return False


def optimized(book: dict, name: str, plan: dict) -> bool:
    return False


def lock(book: dict, name: str) -> bool:
    return False


def copy(book: dict, source: str, name: str) -> bool:
    return False


if __name__ == "__main__":
    book = {}
    print(create(book, "base", {"budget": 900}), checked(book, "base"), optimized(book, "base", {"W1": 2027}))
