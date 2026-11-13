from __future__ import annotations

import highspy


def build(supply: list[float], demand: list[float], cost: list[list[float]], cap: list[list[float]]) -> highspy.HighsLp:
    """The route LP, column by column: variable i * n + j ships from source i to customer j."""
    m, n = len(supply), len(demand)
    lp = highspy.HighsLp()
    # TODO: costs, bounds, the m + n rows and the column-wise matrix (start_, index_, value_).
    return lp


def solve(lp: highspy.HighsLp, solver: str = "ipm") -> tuple[str, float]:
    """Solve with highspy and return (status, objective)."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("solver", solver)
    h.passModel(lp)
    h.run()
    return h.modelStatusToString(h.getModelStatus()), h.getInfo().objective_function_value


if __name__ == "__main__":
    print(solve(build([5, 5], [4, 6], [[1, 3], [2, 1]], [[10, 10], [10, 10]])))
