import math

import pytest

from rows import parse_row

R_ROW = " R       0       0         0   0.00%   1520.5          1490               2.05%        0      0      0        16     0.1s"
L_ROW = " L      25       4        10  55.00%   1498.0          1495               0.20%      300     20     41      1500     0.9s"
BLANK = "        12       3         5  40.00%   1500.25         1492               0.55%      140     12     30       900     0.4s"
FIRST = " z       0       0         0   0.00%   inf             900                Large        0      0      0         0     0.0s"


def test_a_row_from_randomized_rounding():
    row = parse_row(R_ROW)
    assert row == {"src": "R", "nodes": 0, "bound": 1520.5, "incumbent": 1490.0, "gap": pytest.approx(0.0205),
                   "cuts": 0, "lp_iters": 16}


def test_a_row_from_a_sub_mip():
    row = parse_row(L_ROW)
    assert row == {"src": "L", "nodes": 25, "bound": 1498.0, "incumbent": 1495.0, "gap": pytest.approx(0.002),
                   "cuts": 300, "lp_iters": 1500}


def test_a_periodic_row_has_no_source():
    row = parse_row(BLANK)
    assert row is not None
    assert row["src"] == "" and row["nodes"] == 12 and row["bound"] == 1500.25 and row["lp_iters"] == 900


def test_before_the_first_lp_the_bound_is_inf_and_the_gap_is_large():
    row = parse_row(FIRST)
    assert row is not None and row["src"] == "z"
    assert math.isinf(row["bound"]) and row["incumbent"] == 900.0 and row["gap"] is None


def test_lines_that_are_not_progress_rows_give_none():
    others = ["Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
              "Model after restart has 7 rows, 84 cols (84 bin., 0 int., 0 impl., 0 cont., 0 dom.fix.), and 112 nonzeros",
              "  LP iterations     9738",
              "        Nodes      |    B&B Tree     |            Objective Bounds              |  Dynamic Constraints |       Work      ",
              ""]
    got = []
    for line in others:
        try:
            got.append(parse_row(line))
        except Exception as error:      # a parser that raises on a header line is as wrong as one that returns a dict
            got.append(f"raised {type(error).__name__}")
    assert got == [None] * len(others)
    assert parse_row(R_ROW) is not None


def test_any_source_letter_is_accepted():
    row = parse_row(R_ROW.replace(" R ", " Q ", 1))
    assert row is not None and row["src"] == "Q" and row["nodes"] == 0
