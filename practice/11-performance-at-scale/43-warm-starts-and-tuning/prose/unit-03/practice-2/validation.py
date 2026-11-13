from __future__ import annotations


def folds(names: list[str], group_of: dict[str, str], k: int) -> list[list[str]]:
    """k folds for cross-validation: groups dealt round-robin in sorted order, each group kept whole."""
    # TODO: deal whole groups to the folds.
    return [[] for _ in range(k)]


def leaks(train: list[str], test: list[str], group_of: dict[str, str]) -> set[str]:
    """The groups that have instances on both sides of a split."""
    # TODO
    return set()


if __name__ == "__main__":
    group_of = {"elm-jan": "elm", "elm-feb": "elm", "oak-jan": "oak", "ash-jan": "ash"}
    print(folds(list(group_of), group_of, 2))
    print(leaks(["elm-jan", "oak-jan"], ["elm-feb"], group_of))
