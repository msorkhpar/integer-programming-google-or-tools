from __future__ import annotations


def pick(passing: list[str], evidence: dict[str, dict]) -> tuple[str | None, str | None]:
    """(default, fallback): finalists ranked by worst seed spread, then name."""
    # TODO: keep the finalists, rank them, and return the first two.
    return None, None


if __name__ == "__main__":
    evidence = {"Ash": {"solved": 9, "runs": 9, "repeat": True, "spread": 1.4},
                "Elm": {"solved": 9, "runs": 9, "repeat": True, "spread": 1.1}}
    print(pick(["Ash", "Elm"], evidence))
