from __future__ import annotations


def folds(names: list[str], group_of: dict[str, str], k: int) -> list[list[str]]:
    """k folds for cross-validation: groups dealt round-robin in sorted order, each group kept whole."""
    out: list[list[str]] = [[] for _ in range(k)]
    for n, group in enumerate(sorted(set(group_of[name] for name in names))):
        out[n % k].extend(sorted(name for name in names if group_of[name] == group))
    return out


def leaks(train: list[str], test: list[str], group_of: dict[str, str]) -> set[str]:
    """The groups that have instances on both sides of a split."""
    return {group_of[n] for n in train} & {group_of[n] for n in test}


if __name__ == "__main__":
    group_of = {"elm-jan": "elm", "elm-feb": "elm", "oak-jan": "oak", "ash-jan": "ash"}
    print(folds(list(group_of), group_of, 2))
    print(leaks(["elm-jan", "oak-jan"], ["elm-feb"], group_of))
