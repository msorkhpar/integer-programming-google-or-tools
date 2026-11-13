import highspy

from routes import build, solve


def gpu_available() -> bool:
    """The course's answer when its GPU helper is importable (the GPU image adds GPU checks); False otherwise."""
    try:
        from gpu import gpu_available as found
    except ImportError:
        return False
    return found()


SUPPLY, DEMAND = [7.0, 8.0], [4.0, 5.0, 6.0]
COST = [[4.0, 6.0, 9.0], [5.0, 3.0, 2.0]]
LOOSE = [[100.0] * 3, [100.0] * 3]


def test_each_route_column_holds_its_source_row_and_its_customer_row():
    lp = build(SUPPLY, DEMAND, COST, LOOSE)
    assert (lp.num_col_, lp.num_row_) == (6, 5)
    starts, rows = list(lp.a_matrix_.start_), list(lp.a_matrix_.index_)
    assert starts == [0, 2, 4, 6, 8, 10, 12]
    assert [sorted(rows[starts[k]:starts[k + 1]]) for k in range(6)] == [[0, 2], [0, 3], [0, 4], [1, 2], [1, 3], [1, 4]]


def test_the_routes_are_solved_at_the_cheapest_cost():
    lp = build(SUPPLY, DEMAND, COST, LOOSE)
    status, cost = solve(lp, "ipm")
    assert status == "Optimal" and abs(cost - 52.0) <= 1e-6 * 52.0
    if gpu_available():                        # on the GPU image with a GPU: the same LP by GPU PDLP
        status, gpu_cost = solve(lp, "pdlp")
        assert status == "Optimal" and abs(gpu_cost - cost) <= 1e-6 * cost


def test_a_route_capacity_binds_and_raises_the_cost():
    capped = [[100.0] * 3, [100.0, 1.0, 100.0]]          # source 1 to customer 1: at most 1
    status, cost = solve(build(SUPPLY, DEMAND, COST, capped), "ipm")
    assert status == "Optimal" and abs(cost - 56.0) <= 1e-6 * 56.0


def test_spare_supply_may_stay_at_the_source():
    status, cost = solve(build([10.0, 12.0], DEMAND, COST, LOOSE), "ipm")
    assert status == "Optimal" and abs(cost - 43.0) <= 1e-6 * 43.0
