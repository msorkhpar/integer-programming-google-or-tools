from courier import cheapest_runs


def check(runs, deadline, total, plan):
    """Assert the plan keeps every rule and costs `total`."""
    assert set(plan) == set(runs)
    spans = []
    for r, (v, s) in plan.items():
        hours, costs = runs[r]
        assert isinstance(v, int) and 0 <= v < len(hours), f"{r} has no vehicle {v}"
        assert isinstance(s, int) and 0 <= s and s + hours[v] <= deadline, f"{r} ends after the deadline"
        spans.append((s, s + hours[v], r))
    spans.sort()
    for (s1, e1, r1), (s2, e2, r2) in zip(spans, spans[1:]):
        assert e1 <= s2, f"{r1} and {r2} overlap"
    assert total == sum(runs[r][1][v] for r, (v, _) in plan.items())


def test_a_loose_deadline_takes_the_cheapest_vehicles():
    runs = {"a": ([4, 2], [20, 35]), "b": ([3, 1], [15, 30]), "c": ([2, 1], [10, 12])}
    total, plan = cheapest_runs(runs, 30)
    assert total == 45
    assert {r: v for r, (v, _) in plan.items()} == {"a": 0, "b": 0, "c": 0}


def test_every_run_gets_a_vehicle_and_a_start():
    runs = {"a": ([3, 1], [5, 9])}
    total, plan = cheapest_runs(runs, 10)
    assert set(plan) == {"a"}
    v, s = plan["a"]
    assert v in (0, 1) and isinstance(s, int) and s >= 0


def test_a_tight_deadline_buys_faster_vehicles():
    runs = {"a": ([4, 2], [20, 35]), "b": ([3, 1], [15, 30]), "c": ([2, 1], [10, 12])}
    # 9 hours: one run must speed up; the cheapest saving is c (1 hour for $2).
    total, plan = cheapest_runs(runs, 8)
    check(runs, 8, total, plan)
    assert total == 47
    # 5 hours: four hours to save, and only the fast a and b together save that many.
    total, plan = cheapest_runs(runs, 5)
    check(runs, 5, total, plan)
    assert total == 75


def test_the_runs_never_overlap():
    runs = {"a": ([3, 1], [10, 40]), "b": ([3, 1], [10, 40])}
    total, plan = cheapest_runs(runs, 4)
    check(runs, 4, total, plan)
    assert total == 50
