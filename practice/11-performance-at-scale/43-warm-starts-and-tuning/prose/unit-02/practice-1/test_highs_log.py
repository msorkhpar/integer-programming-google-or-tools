from highs_log import incumbents

HEADER = [
    "Presolving model",
    "120 rows, 300 cols, 900 nonzeros  0s",
    "Src: B => Branching; C => Central rounding; F => Feasibility pump; H => Heuristic;",
    "        Nodes      |    B&B Tree     |            Objective Bounds              |  Dynamic Constraints |       Work      ",
    "Src  Proc. InQueue |  Leaves   Expl. | BestBound       BestSol              Gap |   Cuts   InLp Confl. | LpIters     Time",
    "",
]
ROWS = [
    "         0       0         0   0.00%   0               inf                  inf        0      0      0         0     0.0s",
    " J       0       0         0   0.00%   0               9120               Large        0      0      0         0     0.0s",
    " R       0       0         0   0.00%   7650.25         8410               9.04%        0      0      0        57     0.0s",
    "         0       0         0   0.00%   7702.5          8410               8.41%       14      9      0       180     0.1s",
    " L       0       0         0   0.00%   7702.5          7790               1.13%      31     22      4       402     0.2s",
]
RESTART = ["", "12.0% inactive integer columns, restarting",
           "Model after restart has 100 rows, 260 cols (260 bin., 0 int., 0 impl., 0 cont., 0 dom.fix.), and 700 nonzeros", ""]
TAIL = [
    " T      85       3        40  91.20%   7760            7765               0.06%      55     30    210      4120     0.9s",
    "        97       0        48 100.00%   7765            7765               0.00%      55     30    233      4410     1.0s",
    "",
    "Solving report",
    "  Primal bound      7765",
    "  LP iterations     4410 (total)",
]
PLAIN = HEADER + [ROWS[1], ROWS[2], ROWS[4], TAIL[0]] + TAIL[2:]


def test_each_better_plan_is_read_with_its_lp_iterations():
    assert incumbents(PLAIN) == [(0.0, 9120.0), (57.0, 8410.0), (402.0, 7790.0), (4120.0, 7765.0)]


def test_a_maximization_log_counts_higher_plans_as_better():
    log = HEADER + [
        " J       0       0         0   0.00%   900             310                Large        0      0      0         0     0.0s",
        " L       0       0         0   0.00%   880             600               46.67%        0      0      0        90     0.0s",
        " H       0       0         0   0.00%   880             550               60.00%        0      0      0       120     0.0s",
    ]
    assert incumbents(log, minimize=False) == [(0.0, 310.0), (90.0, 600.0)]


def test_a_row_with_no_plan_yet_is_skipped():
    assert incumbents(HEADER + ROWS[:2]) == [(0.0, 9120.0)]


def test_a_row_that_repeats_the_best_plan_is_not_a_new_one():
    assert [w for w, _ in incumbents(HEADER + ROWS[1:] + TAIL)] == [0.0, 57.0, 402.0, 4120.0]


def test_lines_before_the_table_are_not_rows():
    log = ["12 rows, 30 cols, 90 nonzeros, 1 2 3 4 5 6 7 8  0.0s"] + HEADER + ROWS[1:2]
    assert incumbents(log) == [(0.0, 9120.0)]


def test_the_restart_message_inside_the_table_is_skipped():
    assert incumbents(HEADER + ROWS[1:2] + RESTART + TAIL[:1]) == [(0.0, 9120.0), (4120.0, 7765.0)]


def test_a_start_shown_on_a_row_without_a_source_letter_counts():
    log = HEADER + ["         0       0         0   0.00%   7600            7820              2.81%        0      0      0         0     0.0s"]
    assert incumbents(log) == [(0.0, 7820.0)]


def test_lp_iterations_printed_in_thousands_are_read_in_full():
    # three rows of a long HiGHS run, as printed: past about a million, LpIters gets a "k" suffix
    log = HEADER + [
        " T  303210   10339    125244  66.04%   0               1                100.00%      555     12   5414    895704    42.4s",
        "    339550   10360    141291  70.97%   0               1                100.00%      554      6   4096     1003k    47.4s",
        " L  374863   10550    156710  75.18%   0               0.999999         100.00%      644     12   3574     1107k    53.7s",
    ]
    assert incumbents(log) == [(895704.0, 1.0), (1107000.0, 0.999999)]
