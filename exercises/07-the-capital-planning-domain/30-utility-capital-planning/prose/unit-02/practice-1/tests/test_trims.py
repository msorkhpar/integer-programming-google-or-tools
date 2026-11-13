from trims import plan_trims

# A municipal utility's circuits: id -> (miles, year last trimmed). Not the lesson's circuits.


def test_everything_due_fits_in_capacity():
    circuits = {"A": (10, 2020), "B": (20, 2021), "C": (5, 2022)}
    assert plan_trims(circuits, 3, 100, [2023, 2024, 2025, 2026]) == {
        2023: (["A"], 0), 2024: (["B"], 0), 2025: (["C"], 0), 2026: (["A"], 0)}


def test_backlog_is_the_due_miles_left():
    circuits = {"A": (30, 2019), "B": (30, 2020), "C": (30, 2021)}
    assert plan_trims(circuits, 3, 40, [2024, 2025, 2026]) == {
        2024: (["A"], 60), 2025: (["B"], 30), 2026: (["C"], 0)}


def test_most_overdue_goes_first():
    circuits = {"A": (10, 2022), "B": (10, 2019)}
    assert plan_trims(circuits, 3, 10, [2025, 2026]) == {2025: (["B"], 10), 2026: (["A"], 0)}


def test_a_circuit_too_big_does_not_block_smaller_ones():
    circuits = {"A": (50, 2018), "B": (10, 2019), "C": (10, 2020)}
    assert plan_trims(circuits, 3, 25, [2024]) == {2024: (["B", "C"], 50)}


def test_a_circuit_no_year_can_trim_stays_in_the_backlog():
    circuits = {"A": (50, 2018), "B": (10, 2019)}
    assert plan_trims(circuits, 3, 25, [2024, 2025, 2026]) == {
        2024: (["B"], 50), 2025: ([], 50), 2026: ([], 50)}
