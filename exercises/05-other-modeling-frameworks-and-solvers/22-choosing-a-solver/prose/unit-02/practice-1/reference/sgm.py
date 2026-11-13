from __future__ import annotations

import math


def shifted_geometric_mean(values: list[float], shift: float) -> float:
    """exp(mean of ln(max(1, v + shift))) - shift."""
    logs = [math.log(max(1.0, v + shift)) for v in values]
    return math.exp(sum(logs) / len(logs)) - shift


if __name__ == "__main__":
    print(shifted_geometric_mean([0.5, 4.0, 120.0], 10.0))
