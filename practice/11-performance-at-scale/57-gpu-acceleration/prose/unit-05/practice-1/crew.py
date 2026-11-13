from __future__ import annotations

import highspy


def build(values: list[float], hours: list[list[float]], capacity: list[float],
          requires: list[tuple[int, int]]) -> highspy.HighsLp:
    """The crew's job selection: x_j = 1 if job j is done this year."""
    lp = highspy.HighsLp()
    # TODO: binary columns worth values[j], a crew row per quarter, a row per (a, b) in requires.
    return lp


def solve(lp: highspy.HighsLp, fixed: dict[int, int] | None = None) -> tuple[str, float, list[float]]:
    """Solve on one thread (so a rerun repeats); `fixed` pins some jobs to 0 or 1 first."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.passModel(lp)
    for j, v in (fixed or {}).items():
        h.changeColBounds(j, float(v), float(v))
    h.run()
    return h.modelStatusToString(h.getModelStatus()), h.getInfo().objective_function_value, list(h.getSolution().col_value)


if __name__ == "__main__":
    print(solve(build([5, 4], [[2, 0], [1, 1]], [2, 1], [(0, 1)])))
