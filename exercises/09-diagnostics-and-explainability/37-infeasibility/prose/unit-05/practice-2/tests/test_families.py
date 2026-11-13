from families import two_pass


def oracle(*clashes):
    sets = [set(c) for c in clashes]
    return lambda on: any(c <= set(on) for c in sets)


FAMILIES = {
    "sensor": ["sensor_N1", "sensor_N2"],
    "uptime": ["uptime_99"],
    "budget": ["budget_q1", "budget_q2"],
    "staff": ["staff_min_3"],
}


def test_the_families_and_the_rules_of_one_conflict_are_found():
    kept, conflict = two_pass(FAMILIES, oracle(["sensor_N2", "budget_q1"]))
    assert kept == ["sensor", "budget"]
    assert conflict == ["sensor_N2", "budget_q1"]


def test_a_family_dropped_in_the_first_pass_stays_dropped():
    # Two separate conflicts, each across two families: one of them must survive whole.
    kept, conflict = two_pass(FAMILIES, oracle(["sensor_N1", "uptime_99"], ["budget_q2", "staff_min_3"]))
    assert kept == ["budget", "staff"]
    assert conflict == ["budget_q2", "staff_min_3"]


def test_the_second_pass_switches_dropped_families_off():
    # Inside the budget family, both quarters clash; budget_q1 also clashes with staff alone.
    kept, conflict = two_pass(FAMILIES, oracle(["budget_q1", "budget_q2"], ["budget_q1", "staff_min_3"]))
    assert kept == ["budget"]
    assert conflict == ["budget_q1", "budget_q2"]
