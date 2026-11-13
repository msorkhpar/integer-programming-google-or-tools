from steady import Project, allowed

YEARS = [2027, 2028, 2029, 2030]
STEP = 100
RELINING = [
    Project("R1", (80, 80), (2027, 2028, 2029)),
    Project("R2", (120,), (2027, 2028, 2029, 2030)),
    Project("R3", (50, 50, 50), (2027, 2028)),
    Project("R4", (200,), (2028, 2029, 2030)),
    Project("R5", (90,), (2027, 2028, 2029, 2030)),
    Project("R6", (60, 60), (2027, 2028, 2029)),
]


def ok(schedule: dict[str, int]) -> bool:
    return allowed(RELINING, YEARS, STEP, schedule)


def test_a_steady_plan_is_allowed_and_a_jump_is_refused():
    assert ok({"R3": 2027, "R6": 2028, "R5": 2030}) is True        # spends 50, 110, 110, 90
    assert ok({"R5": 2027, "R4": 2028}) is False                   # spends 90, 200, 0, 0


def test_a_drop_beyond_the_step_is_refused():
    assert ok({"R3": 2027, "R6": 2028, "R5": 2030}) is True        # spends 50, 110, 110, 90
    assert ok({"R6": 2027, "R2": 2029}) is False                   # spends 60, 60, 120, 0


def test_each_year_is_compared_with_the_year_before():
    assert ok({"R3": 2028, "R6": 2029}) is True                    # spends 0, 50, 110, 110
    assert ok({"R5": 2027, "R4": 2028}) is False                   # spends 90, 200, 0, 0


def test_the_last_pair_of_years_is_checked():
    assert ok({"R3": 2027, "R6": 2028, "R5": 2030}) is True        # spends 50, 110, 110, 90
    assert ok({"R6": 2027, "R3": 2028, "R2": 2030}) is False       # spends 60, 110, 50, 170


def test_a_change_of_exactly_the_step_is_allowed():
    assert ok({"R1": 2027, "R2": 2029, "R5": 2030, "R6": 2029}) is True   # spends 80, 80, 180, 150
    assert ok({"R5": 2027, "R4": 2028}) is False                          # spends 90, 200, 0, 0
