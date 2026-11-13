from __future__ import annotations

import pandas as pd


def hours_entries(options: pd.DataFrame, profile: pd.DataFrame, weeks: list[int]) -> pd.DataFrame:
    """The nonzeros of the weekly crew-hours rows, one table row each: week, col, coef.

    `options` has one row per variable y[task, start], columns `task` and `start`; the variable's
    column number `col` is its position in `options`, counting from 0. `profile` has columns `task`,
    `k` and `hours`: the crew-hours a task needs in its k-th week of work (k = 0 is its start week).
    """
    cols = options[["task", "start"]].reset_index(drop=True)
    cols["col"] = cols.index
    terms = cols.merge(profile, on="task")
    terms["week"] = terms["start"] + terms["k"]
    terms = terms[terms["week"].isin(weeks) & (terms["hours"] != 0)]
    out = terms.sort_values(["week", "col"])[["week", "col", "hours"]].rename(columns={"hours": "coef"})
    out["coef"] = out["coef"].astype(float)
    return out.reset_index(drop=True)


if __name__ == "__main__":
    options = pd.DataFrame({"task": ["T1", "T1", "T2"], "start": [1, 2, 1]})
    profile = pd.DataFrame({"task": ["T1", "T1", "T2"], "k": [0, 1, 0], "hours": [5, 3, 4]})
    print(hours_entries(options, profile, [1, 2, 3]).to_string(index=False))
