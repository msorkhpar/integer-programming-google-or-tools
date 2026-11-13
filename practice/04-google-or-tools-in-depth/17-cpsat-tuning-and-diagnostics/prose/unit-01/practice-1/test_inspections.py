from itertools import combinations

from inspections import Job, improve

# A utility's substation inspections, not the lesson's portfolio.
WEEK = [Job("A1", "north", 30, 10), Job("A2", "north", 25, 10), Job("A3", "north", 10, 10),
        Job("B1", "south", 50, 20), Job("B2", "south", 5, 30)]
NORTH = {"A1", "A2", "A3"}


def value(jobs, plan):
    return sum(j.value for j in jobs if j.name in plan)


def best_inside(jobs, hours, plan, free):
    """Brute force: the best value with every job outside `free` kept as `plan` has it."""
    kept = {j.name for j in jobs if j.name in plan and j.name not in free}
    loose = [j for j in jobs if j.name in free]
    best = None
    for r in range(len(loose) + 1):
        for chosen in combinations(loose, r):
            names = kept | {j.name for j in chosen}
            if sum(j.hours for j in jobs if j.name in names) <= hours:
                best = max(best or 0, value(jobs, names))
    return best


def test_the_result_is_the_best_plan_inside_the_neighborhood():
    result = improve(WEEK, 40, {"A3", "B1"}, NORTH)
    assert value(WEEK, result) == best_inside(WEEK, 40, {"A3", "B1"}, NORTH) == 105
    assert sum(j.hours for j in WEEK if j.name in result) <= 40


def test_an_empty_neighborhood_returns_the_plan_unchanged():
    assert improve(WEEK, 40, {"A1", "A2", "B1"}, set()) == {"A1", "A2", "B1"}


def test_a_job_the_plan_leaves_out_stays_out_unless_it_is_free():
    week = WEEK + [Job("B3", "south", 40, 5)]
    result = improve(week, 40, {"A3", "B1"}, NORTH)
    assert "B3" not in result
    assert value(week, result) == 105


def test_a_job_the_plan_keeps_stays_in_unless_it_is_free():
    week = WEEK + [Job("A4", "north", 60, 20)]
    result = improve(week, 40, {"A3", "B1"}, NORTH | {"A4"})
    assert "B1" in result
    assert value(week, result) == 110
