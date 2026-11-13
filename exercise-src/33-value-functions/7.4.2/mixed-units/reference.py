from __future__ import annotations

#: unit -> (what it measures, how many base units one of it is)
UNITS = {
    "minutes": ("time", 1.0), "hours": ("time", 60.0),
    "complaints": ("count", 1.0), "dozen complaints": ("count", 12.0),
    "$": ("money", 1.0), "$k": ("money", 1_000.0),
}


def in_base(amount: float, unit: str) -> float:
    """An amount restated in its kind's base unit (minutes, complaints, dollars)."""
    return amount * UNITS[unit][1]


def score(benefit: dict, reference: dict, weights: dict[str, float]) -> float:
    """Weighted sum of each measure's benefit over its reference; both are {measure: (amount, unit)}."""
    total = 0.0
    for measure, (amount, unit) in benefit.items():
        ref_amount, ref_unit = reference[measure]
        total += weights[measure] * in_base(amount, unit) / in_base(ref_amount, ref_unit)
    return total


def rank(projects: dict[str, dict], reference: dict, weights: dict[str, float]) -> list[str]:
    """Project names from the highest score to the lowest; equal scores in name order."""
    scores = {name: score(benefit, reference, weights) for name, benefit in projects.items()}
    return sorted(scores, key=lambda name: (-scores[name], name))


if __name__ == "__main__":
    reference = {"time": (500, "hours"), "complaints": (40, "complaints"), "savings": (200, "$k")}
    weights = {"time": 0.5, "complaints": 0.2, "savings": 0.3}
    stop = {"time": (12_000, "minutes"), "complaints": (10, "complaints"), "savings": (50_000, "$")}
    print(score(stop, reference, weights))
