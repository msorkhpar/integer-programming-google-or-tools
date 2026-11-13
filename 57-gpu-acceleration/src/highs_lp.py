"""Hand HiGHS a whole model at once as a `highspy.HighsLp`: costs, bounds, rows, the matrix column-wise or
row-wise, an integer column and the sense. The model is a three-variable toy, not GridCap data:

    maximise   5 x0 + 4 x1 + 2 x2
    subject to 2 x0 + 3 x1 +   x2 <= 5      (cap)
                 x0 +   x1 + 2 x2 >= 1      (need)
               x0 >= 0 integer, 0 <= x1 <= 1, x2 >= 0
"""

import highspy


def build(colwise: bool, integer: bool = True) -> highspy.HighsLp:
    """The toy model as a HighsLp, its matrix stored column by column or row by row."""
    inf = highspy.kHighsInf
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = 3, 2
    lp.col_cost_ = [5.0, 4.0, 2.0]
    lp.col_lower_ = [0.0, 0.0, 0.0]
    lp.col_upper_ = [inf, 1.0, inf]                     # kHighsInf: no upper bound
    lp.row_lower_ = [-inf, 1.0]                         # cap has no lower side
    lp.row_upper_ = [5.0, inf]                          # need has no upper side
    if colwise:                                         # column k's entries sit at start_[k] .. start_[k+1]-1
        lp.a_matrix_.format_ = highspy.MatrixFormat.kColwise
        lp.a_matrix_.start_ = [0, 2, 4, 6]
        lp.a_matrix_.index_ = [0, 1, 0, 1, 0, 1]        # the row of each entry
        lp.a_matrix_.value_ = [2.0, 1.0, 3.0, 1.0, 1.0, 2.0]
    else:                                               # row r's entries sit at start_[r] .. start_[r+1]-1
        lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
        lp.a_matrix_.start_ = [0, 3, 6]
        lp.a_matrix_.index_ = [0, 1, 2, 0, 1, 2]        # the column of each entry
        lp.a_matrix_.value_ = [2.0, 3.0, 1.0, 1.0, 1.0, 2.0]
    if integer:                                         # leave integrality_ unset for an LP
        lp.integrality_ = [highspy.HighsVarType.kInteger, highspy.HighsVarType.kContinuous,
                           highspy.HighsVarType.kContinuous]
    lp.sense_ = highspy.ObjSense.kMaximize              # kMinimize for a minimisation
    return lp


def solve(lp: highspy.HighsLp) -> tuple[str, float, list[float]]:
    """Pass the whole model to HiGHS, solve on one thread, and return (status, objective, x)."""
    h = highspy.Highs()
    h.setOptionValue("output_flag", False)
    h.setOptionValue("threads", 1)
    h.passModel(lp)
    h.run()
    return h.modelStatusToString(h.getModelStatus()), h.getInfo().objective_function_value, list(h.getSolution().col_value)


def main() -> None:
    for name, lp in (("column-wise, x0 integer", build(True)), ("row-wise, x0 integer", build(False)),
                     ("column-wise, x0 continuous", build(True, integer=False))):
        status, objective, x = solve(lp)
        print(f"{name:27s} {status}, objective {objective:g}, x = {[round(v, 6) for v in x]}")


if __name__ == "__main__":
    main()
