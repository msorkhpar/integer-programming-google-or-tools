from depot import plan_depot


def check(buses, start):
    """Assert the plan keeps every rule; return the hour the last bus leaves."""
    assert set(start) == {(b, k) for b, steps in buses.items() for k in range(len(steps))}
    by_bay = {}
    for b, steps in buses.items():
        for k, (bay, hours) in enumerate(steps):
            assert isinstance(start[b, k], int) and start[b, k] >= 0
            by_bay.setdefault(bay, []).append((start[b, k], start[b, k] + hours, b))
            if k:
                assert start[b, k] >= start[b, k - 1] + steps[k - 1][1], f"{b} step {k} starts before step {k - 1} ends"
    for bay, spans in by_bay.items():
        spans.sort()
        for (s1, e1, b1), (s2, e2, b2) in zip(spans, spans[1:]):
            assert e1 <= s2, f"{b1} and {b2} overlap on {bay}"
    return max(start[b, len(steps) - 1] + steps[-1][1] for b, steps in buses.items())


def test_every_step_gets_a_start():
    buses = {"b1": [("wash", 2)], "b2": [("service", 3)]}
    start = plan_depot(buses)
    assert set(start) == {("b1", 0), ("b2", 0)}
    assert all(isinstance(s, int) and s >= 0 for s in start.values())


def test_buses_on_their_own_bays_run_together():
    buses = {"b1": [("wash", 2)], "b2": [("service", 3)], "b3": [("inspect", 1)]}
    start = plan_depot(buses)
    assert start == {("b1", 0): 0, ("b2", 0): 0, ("b3", 0): 0}


def test_a_shared_bay_takes_one_bus_at_a_time():
    buses = {"b1": [("service", 3)], "b2": [("service", 2)], "b3": [("wash", 1)]}
    assert check(buses, plan_depot(buses)) == 5


def test_a_bus_finishes_a_step_before_the_next():
    buses = {"b1": [("wash", 2), ("service", 3), ("inspect", 1)],
             "b2": [("service", 2), ("wash", 2)],
             "b3": [("inspect", 2), ("wash", 1)]}
    # b1's three steps take 6 hours end to end, and the other buses fit around it.
    assert check(buses, plan_depot(buses)) == 6
