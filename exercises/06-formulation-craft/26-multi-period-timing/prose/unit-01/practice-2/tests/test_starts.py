from starts import Project, ScheduleError, deferrals, read_starts

# A gas utility's main replacements, not the lesson's portfolio.
MAINS = [
    Project("G1", (2027, 2028, 2029)),
    Project("G2", (2028, 2029)),
    Project("G3", (2027,)),
    Project("G4", (2027, 2028)),
]


def values_for(schedule: dict[str, int]) -> dict[tuple[str, int], float]:
    """Exact 0/1 values for a schedule: project id -> start year."""
    return {(p.pid, t): 1.0 if schedule.get(p.pid) == t else 0.0 for p in MAINS for t in p.starts}


def read(values: dict[tuple[str, int], float]):
    """The start years, or "refused" if read_starts raised ScheduleError."""
    try:
        return read_starts(values, MAINS)
    except ScheduleError:
        return "refused"


WHOLE = values_for({"G1": 2029, "G2": 2028, "G3": 2027})


def test_each_project_gets_its_start_year_or_none():
    assert read(WHOLE) == {"G1": 2029, "G2": 2028, "G3": 2027, "G4": None}


def test_deferrals_count_years_after_the_earliest_start():
    late = values_for({"G1": 2029, "G4": 2028})
    assert deferrals(read_starts(late, MAINS), MAINS) == {"G1": 2, "G4": 1}


def test_values_within_tolerance_of_whole_numbers_are_read():
    near = dict(WHOLE)
    near["G1", 2029] = 0.9999999
    near["G4", 2027] = 1e-9
    assert read(WHOLE) == {"G1": 2029, "G2": 2028, "G3": 2027, "G4": None}
    assert read(near) == {"G1": 2029, "G2": 2028, "G3": 2027, "G4": None}


def test_a_fractional_value_is_refused():
    half = dict(WHOLE)
    half["G4", 2027] = 0.5
    assert read(WHOLE) != "refused" and read(WHOLE).get("G4", "missing") is None
    assert read(half) == "refused"


def test_a_project_started_twice_is_refused():
    twice = dict(WHOLE)
    twice["G1", 2027] = 1.0
    assert read(WHOLE) != "refused"
    assert read(twice) == "refused"


def test_a_project_started_on_time_is_not_a_deferral():
    on_time = values_for({"G1": 2027, "G2": 2029, "G3": 2027})
    assert deferrals(read_starts(on_time, MAINS), MAINS) == {"G2": 1}
