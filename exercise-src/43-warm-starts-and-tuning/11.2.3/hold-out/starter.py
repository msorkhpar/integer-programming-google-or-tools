from __future__ import annotations

import math


def sgm(values: list[float], shift: float) -> float:
    """The shifted geometric mean of lesson 5.4.2: exp(mean of ln(max(1, v + shift))) - shift."""
    return math.exp(sum(math.log(max(1.0, v + shift)) for v in values) / len(values)) - shift


def score(work: dict[tuple[str, str], float], config: str, instances: list[str], shift: float) -> float:
    """SGM of one configuration's work over some instances; work[(instance, config)]."""
    # TODO
    return 0.0


def tune(work: dict[tuple[str, str], float], configs: list[str], train: list[str], test: list[str],
         shift: float) -> tuple[str, float, float]:
    """Pick the configuration with the best score on `train` (ties to the earlier one; configs[0] is the
    default), and return it with its train and test scores as ratios to the default's."""
    # TODO: choose on the training instances only, then report both ratios to the default.
    return "", 0.0, 0.0


if __name__ == "__main__":
    work = {("w1", "default"): 900.0, ("w1", "fast"): 500.0, ("w2", "default"): 800.0, ("w2", "fast"): 950.0}
    print(tune(work, ["default", "fast"], ["w1"], ["w2"], shift=100))
