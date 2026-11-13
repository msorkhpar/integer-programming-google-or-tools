from __future__ import annotations


def screen(features: set[str], table: dict[str, dict[str, set[str]]]) -> dict[str, str]:
    """Per solver: "refuses <f>", else "alters <f>", else "ok", for the features the model uses."""
    verdicts = {}
    for solver, gaps in table.items():
        refused = sorted(features & gaps["refuses"])
        altered = sorted(features & gaps["alters"])
        if refused:
            verdicts[solver] = f"refuses {refused[0]}"
        elif altered:
            verdicts[solver] = f"alters {altered[0]}"
        else:
            verdicts[solver] = "ok"
    return verdicts


if __name__ == "__main__":
    table = {"Alder": {"refuses": {"quadratic"}, "alters": set()}, "Birch": {"refuses": set(), "alters": set()}}
    print(screen({"quadratic"}, table))
