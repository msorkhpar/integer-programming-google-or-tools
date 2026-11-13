from __future__ import annotations

import math


def sgm(values: list[float], shift: float) -> float:
    """The shifted geometric mean of lesson 5.4.2: exp(mean of ln(max(1, v + shift))) - shift."""
    return math.exp(sum(math.log(max(1.0, v + shift)) for v in values) / len(values)) - shift


def score(work: dict[tuple[str, str], float], config: str, instances: list[str], shift: float) -> float:
    """SGM of one configuration's work over some instances; work[(instance, config)]."""
    return sgm([work[i, config] for i in instances], shift)


def tune(work: dict[tuple[str, str], float], configs: list[str], train: list[str], test: list[str],
         shift: float) -> tuple[str, float, float]:
    """Pick the configuration with the best score on `train` (ties to the earlier one; configs[0] is the
    default), and return it with its train and test scores as ratios to the default's."""
    default = configs[0]
    chosen = min(configs, key=lambda c: score(work, c, train, shift))
    on_train = score(work, chosen, train, shift) / score(work, default, train, shift)
    on_test = score(work, chosen, test, shift) / score(work, default, test, shift)
    return chosen, on_train, on_test


if __name__ == "__main__":
    work = {("w1", "default"): 900.0, ("w1", "fast"): 500.0, ("w2", "default"): 800.0, ("w2", "fast"): 950.0}
    print(tune(work, ["default", "fast"], ["w1"], ["w2"], shift=100))
