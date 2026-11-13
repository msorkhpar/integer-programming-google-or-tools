from __future__ import annotations


def screen(features: set[str], table: dict[str, dict[str, set[str]]]) -> dict[str, str]:
    """Per solver: "refuses <f>", else "alters <f>", else "ok", for the features the model uses."""
    # TODO: check refusals first, then quiet changes; name the alphabetically first feature.
    return {solver: "ok" for solver in table}


if __name__ == "__main__":
    table = {"Alder": {"refuses": {"quadratic"}, "alters": set()}, "Birch": {"refuses": set(), "alters": set()}}
    print(screen({"quadratic"}, table))
