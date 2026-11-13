from run_bytes import repeats

RUN = {"started_at": "2027-03-01T09:00:00", "stats": {"wall_seconds": 1.25, "nodes": 40}, "cost": 512.0,
       "routes": {"t1": ["depot", "a", "b", "depot"], "t2": ["depot", "c", "depot"]}, "unserved": {"d", "e"}}


def run(**fields):
    return {**RUN, **fields}


def test_runs_differing_only_in_start_time_repeat_and_a_moved_stop_does_not():
    assert repeats([RUN, run(started_at="2027-03-02T14:30:00", unserved={"e", "d"})]) is True
    moved = {"t1": ["depot", "a", "depot"], "t2": ["depot", "c", "b", "depot"]}
    assert repeats([RUN, run(routes=moved)]) is False


def test_the_nested_clock_field_is_left_out():
    assert repeats([RUN, run(stats={"wall_seconds": 3.9, "nodes": 40})]) is True
    assert repeats([RUN, run(stats={"wall_seconds": 1.25, "nodes": 41})]) is False


def test_float_noise_below_a_millionth_is_not_a_difference():
    assert repeats([RUN, run(cost=512.0000000001)]) is True
    assert repeats([RUN, run(cost=512.01)]) is False


def test_minus_zero_and_zero_are_the_same():
    assert repeats([run(cost=0.0), run(cost=-0.0)]) is True
    assert repeats([run(cost=0.0), run(cost=0.5)]) is False


def test_the_order_of_a_route_matters():
    assert repeats([RUN, run(routes={"t2": ["depot", "c", "depot"], "t1": ["depot", "a", "b", "depot"]})]) is True
    assert repeats([RUN, run(routes={**RUN["routes"], "t1": ["depot", "b", "a", "depot"]})]) is False
