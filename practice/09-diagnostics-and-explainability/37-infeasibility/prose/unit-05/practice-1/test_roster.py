from ortools.sat.python import cp_model

from roster import named_conflict


def infeasible_with(rules, nurses, need, max_shifts):
    """Our own check: is the roster infeasible with only these rules?"""
    model = cp_model.CpModel()
    works = {(n, d): model.new_bool_var(f"{n}_{d}") for n in nurses for d in need}
    for rule in rules:
        kind, *rest = rule.split("_")
        if kind == "cover":
            d = int(rest[0])
            model.add(sum(works[n, d] for n in nurses) >= need[d])
        elif kind == "max":
            model.add(sum(works[rest[0], d] for d in need) <= max_shifts[rest[0]])
        elif kind == "off":
            model.add(works[rest[0], int(rest[1])] == 0)
    return cp_model.CpSolver().solve(model) == cp_model.INFEASIBLE


NURSES = ["Ana", "Ben", "Cho"]
EASY = {"Ana": 3, "Ben": 3, "Cho": 3}


def test_a_feasible_roster_gives_none_and_an_impossible_day_is_named():
    assert named_conflict(NURSES, {1: 2, 2: 2, 3: 1}, EASY, []) is None
    found = named_conflict(NURSES, {1: 2, 2: 4, 3: 1}, EASY, [])
    assert found is not None and "cover_2" in found
    assert infeasible_with(found, NURSES, {1: 2, 2: 4, 3: 1}, EASY)


def test_a_day_off_frees_that_day_only():
    need = {1: 2, 2: 2, 3: 2}
    off = [("Ana", 1), ("Ben", 2), ("Cho", 3)]
    assert named_conflict(NURSES, need, EASY, off) is None
    found = named_conflict(NURSES, need, EASY, off + [("Cho", 1)])
    assert found is not None and infeasible_with(found, NURSES, need, EASY)
    assert {"cover_1", "off_Ana_1", "off_Cho_1"} <= set(found)


def test_a_shift_limit_counts_every_day_of_the_week():
    need = {1: 3, 2: 3, 3: 1}
    tight = {"Ana": 1, "Ben": 3, "Cho": 3}
    found = named_conflict(NURSES, need, tight, [])
    assert found is not None and "max_Ana" in found
    assert infeasible_with(found, NURSES, need, tight)


def test_a_day_off_outside_the_roster_forbids_nothing():
    found = named_conflict(NURSES, {1: 2, 2: 4}, EASY, [("Ana", 7)])     # day 2 needs more nurses than exist
    assert found is not None and "cover_2" in found
    assert not any(name.startswith("off_") for name in found)
    assert named_conflict(NURSES, {1: 2, 2: 2}, EASY, [("Ana", 7)]) is None
