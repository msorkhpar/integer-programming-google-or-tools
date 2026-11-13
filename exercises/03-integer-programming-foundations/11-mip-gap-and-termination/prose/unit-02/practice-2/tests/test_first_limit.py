from first_limit import where_it_stops

TRACE = [
    {"seconds": 0.1, "nodes": 0, "solutions": 0, "incumbent": None, "bound": 1200.0},
    {"seconds": 0.4, "nodes": 0, "solutions": 1, "incumbent": 900.0, "bound": 1150.0},
    {"seconds": 2.0, "nodes": 50, "solutions": 2, "incumbent": 1000.0, "bound": 1100.0},
    {"seconds": 9.0, "nodes": 400, "solutions": 3, "incumbent": 1040.0, "bound": 1080.0},
    {"seconds": 30.0, "nodes": 2000, "solutions": 4, "incumbent": 1050.0, "bound": 1060.0},
]


def test_a_relative_gap_stops_the_run_before_its_time_limit():
    assert where_it_stops(TRACE, {"relative_gap": 0.05, "seconds": 60}) == (3, "relative_gap")


def test_a_solution_limit_stops_at_the_row_that_reaches_it():
    assert where_it_stops(TRACE, {"solutions": 2, "seconds": 60}) == (2, "solutions")


def test_a_gap_rule_wins_a_tie_with_a_count_on_the_same_row():
    assert where_it_stops(TRACE, {"relative_gap": 0.1, "nodes": 50}) == (2, "relative_gap")


def test_an_absolute_gap_can_stop_a_run_the_relative_gap_would_not():
    assert where_it_stops(TRACE, {"relative_gap": 0.01, "absolute_gap": 100}) == (2, "absolute_gap")


def test_a_node_limit_is_met_when_the_count_equals_it():
    assert where_it_stops(TRACE, {"nodes": 400}) == (3, "nodes")


def test_rows_without_an_incumbent_cannot_meet_a_gap_rule():
    assert where_it_stops(TRACE, {"absolute_gap": 1500}) == (1, "absolute_gap")


def test_a_run_that_meets_no_limit_returns_none():
    assert where_it_stops(TRACE, {"nodes": 5000, "seconds": 100}) == (None, None)
