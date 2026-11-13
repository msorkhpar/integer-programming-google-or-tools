from __future__ import annotations

import highspy


def build(values: list[float], hours: list[list[float]], capacity: list[float],
          requires: list[tuple[int, int]]) -> highspy.HighsLp:
    """The crew's job selection: x_j = 1 if job j is done this year."""
    n, quarters = len(values), len(capacity)
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_ = n
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = list(values), [0.0] * n, [1.0] * n
    lp.integrality_ = [highspy.HighsVarType.kInteger] * n
    starts, index, value, lower, upper = [0], [], [], [], []
    for q in range(quarters):                                  # crew_q: the quarter's hours
        for j in range(n):
            if hours[j][q]:
                index.append(j)
                value.append(float(hours[j][q]))
        starts.append(len(index))
        lower.append(-inf)
        upper.append(float(capacity[q]))
    for a, b in requires:                                      # after_a_b: x_b <= x_a
        index += [b, a]
        value += [1.0, -1.0]
        starts.append(len(index))
        lower.append(-inf)
        upper.append(0.0)
    lp.num_row_ = len(lower)
    lp.row_lower_, lp.row_upper_ = lower, upper
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = starts, index, value
    lp.sense_ = highspy.ObjSense.kMaximize
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
