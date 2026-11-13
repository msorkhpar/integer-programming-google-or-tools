from __future__ import annotations

import highspy


def build(supply: list[float], demand: list[float], cost: list[list[float]], cap: list[list[float]]) -> highspy.HighsLp:
    """The route LP, column by column: variable i * n + j ships from source i to customer j."""
    m, n = len(supply), len(demand)
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = m * n, m + n
    lp.col_cost_ = [float(cost[i][j]) for i in range(m) for j in range(n)]
    lp.col_lower_ = [0.0] * (m * n)
    lp.col_upper_ = [float(cap[i][j]) for i in range(m) for j in range(n)]
    lp.row_lower_ = [-inf] * m + [float(d) for d in demand]          # ship_i: at most the supply
    lp.row_upper_ = [float(s) for s in supply] + [inf] * n           # need_j: at least the demand
    lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
    lp.a_matrix_.start_ = [2 * k for k in range(m * n + 1)]          # two entries per column
    lp.a_matrix_.index_ = [r for i in range(m) for j in range(n) for r in (i, m + j)]
    lp.a_matrix_.value_ = [1.0] * (2 * m * n)
    lp.sense_ = highspy.ObjSense.kMinimize
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
