from __future__ import annotations


def pick(passing: list[str], evidence: dict[str, dict]) -> tuple[str | None, str | None]:
    """(default, fallback): finalists ranked by worst seed spread, then name."""
    finalists = [s for s in passing if s in evidence          # no evidence: never measured, not a finalist
                 and evidence[s]["solved"] == evidence[s]["runs"] and evidence[s]["repeat"]]
    ranked = sorted(finalists, key=lambda s: (evidence[s]["spread"], s))
    ranked += [None, None]
    return ranked[0], ranked[1]


if __name__ == "__main__":
    evidence = {"Ash": {"solved": 9, "runs": 9, "repeat": True, "spread": 1.4},
                "Elm": {"solved": 9, "runs": 9, "repeat": True, "spread": 1.1}}
    print(pick(["Ash", "Elm"], evidence))
