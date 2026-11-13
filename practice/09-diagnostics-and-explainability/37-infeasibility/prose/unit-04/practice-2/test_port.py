from port import fewest_refusals


def valid(vessels, berths, refused, schedule):
    """Every vessel berths once inside its window, no day is over capacity, unrefused requests hold."""
    if set(schedule) != set(vessels):
        return False
    for v, (first, last, wanted) in vessels.items():
        if not first <= schedule[v] <= last or schedule[v] not in berths:
            return False
        if v not in refused and schedule[v] != wanted:
            return False
    return all(sum(1 for d in schedule.values() if d == day) <= count for day, count in berths.items())


def test_requests_that_fit_are_all_granted_and_a_clash_costs_one_refusal():
    calm = {"Aurora": (1, 3, 1), "Borealis": (1, 3, 2), "Cygnus": (2, 3, 3)}
    berths = {1: 1, 2: 1, 3: 1}
    refused, schedule = fewest_refusals(calm, berths)
    assert refused == [] and schedule == {"Aurora": 1, "Borealis": 2, "Cygnus": 3}
    clash = {"Aurora": (1, 3, 1), "Borealis": (1, 3, 1), "Cygnus": (2, 3, 3)}
    refused, schedule = fewest_refusals(clash, berths)
    assert len(refused) == 1


def test_a_refused_vessel_is_still_berthed_on_another_day():
    vessels = {"Aurora": (1, 2, 1), "Borealis": (1, 2, 1)}
    berths = {1: 1, 2: 1}
    refused, schedule = fewest_refusals(vessels, berths)
    assert len(refused) == 1 and valid(vessels, berths, refused, schedule)


def test_a_moved_vessel_stays_inside_its_window():
    vessels = {"Aurora": (1, 2, 1), "Borealis": (1, 2, 1), "Cygnus": (2, 3, 2)}
    berths = {1: 1, 2: 1, 3: 1}
    refused, schedule = fewest_refusals(vessels, berths)
    assert len(refused) == 2 and valid(vessels, berths, refused, schedule)
