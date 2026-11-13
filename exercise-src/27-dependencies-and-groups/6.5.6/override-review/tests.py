from review import Job, conflicts

# A rail depot's jobs, not the lesson's portfolio.
JOBS = {
    "BOGIE": Job((2027, 2028, 2029), "north"),
    "PANTO": Job((2028, 2029), "north"),
    "DOORS": Job((2027, 2028), "south"),
    "HVAC": Job((2029, 2030, 2031), "east", follows="DOORS", lag=2),
    "PAINT": Job((2030, 2031), "west"),
}


def test_a_clean_list_has_no_conflict():
    assert conflicts(JOBS, [("lock", "BOGIE", 2027), ("lock", "DOORS", 2027), ("ban", "PAINT")]) == set()


def test_a_lock_outside_the_window_is_flagged():
    assert conflicts(JOBS, [("lock", "PANTO", 2027), ("lock", "DOORS", 2027)]) == {"PANTO"}


def test_a_lock_and_a_ban_on_one_job_are_flagged():
    assert conflicts(JOBS, [("lock", "PAINT", 2030), ("ban", "PAINT"), ("ban", "BOGIE")]) == {"PAINT"}


def test_two_locks_on_one_crew_in_one_year_are_flagged():
    assert conflicts(JOBS, [("lock", "BOGIE", 2028), ("lock", "PANTO", 2028), ("lock", "DOORS", 2028)]) \
        == {"BOGIE", "PANTO"}


def test_a_lock_too_soon_after_its_predecessor_is_flagged():
    assert conflicts(JOBS, [("lock", "DOORS", 2028), ("lock", "HVAC", 2029)]) == {"HVAC"}


def test_one_crew_in_different_years_is_fine():
    assert conflicts(JOBS, [("lock", "BOGIE", 2027), ("lock", "PANTO", 2028)]) == set()


def test_a_lock_exactly_the_lag_after_is_fine():
    assert conflicts(JOBS, [("lock", "DOORS", 2028), ("lock", "HVAC", 2030)]) == set()
