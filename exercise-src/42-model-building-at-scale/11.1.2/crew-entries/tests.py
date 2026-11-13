import pandas as pd

from entries import hours_entries


def rows(df):
    return [(int(w), int(c), float(h)) for w, c, h in df[["week", "col", "coef"]].itertuples(index=False)]


OPTIONS = pd.DataFrame({"task": ["T1", "T1", "T2"], "start": [1, 2, 1]})
PROFILE = pd.DataFrame({"task": ["T1", "T1", "T2"], "k": [0, 1, 0], "hours": [5, 3, 4]})


def test_each_start_pays_its_profile_in_the_weeks_it_works():
    got = rows(hours_entries(OPTIONS, PROFILE, [1, 2, 3]))
    assert sorted(got) == [(1, 0, 5.0), (1, 2, 4.0), (2, 0, 3.0), (2, 1, 5.0), (3, 1, 3.0)]


def test_entries_come_in_week_order_then_column_order():
    got = rows(hours_entries(OPTIONS, PROFILE, [1, 2, 3]))
    assert got == [(1, 0, 5.0), (1, 2, 4.0), (2, 0, 3.0), (2, 1, 5.0), (3, 1, 3.0)]


def test_work_past_the_last_planning_week_has_no_entry():
    options = pd.DataFrame({"task": ["T1", "T3"], "start": [1, 2]})
    profile = pd.DataFrame({"task": ["T1", "T3", "T3", "T3"], "k": [0, 0, 1, 2], "hours": [5, 2, 7, 6]})
    got = rows(hours_entries(options, profile, [1, 2, 3]))
    assert sorted(got) == [(1, 0, 5.0), (2, 1, 2.0), (3, 1, 7.0)]


def test_a_week_with_no_work_in_the_profile_has_no_entry():
    options = pd.DataFrame({"task": ["T4"], "start": [1]})
    profile = pd.DataFrame({"task": ["T4", "T4", "T4"], "k": [0, 1, 2], "hours": [3, 0, 3]})
    got = rows(hours_entries(options, profile, [1, 2, 3, 4]))
    assert sorted(got) == [(1, 0, 3.0), (3, 0, 3.0)]


def test_columns_count_positions_even_when_the_table_was_filtered():
    everything = pd.DataFrame({"task": ["T0", "T1", "T9", "T1", "T2"], "start": [1, 1, 1, 2, 1]})
    options = everything[everything["task"] != "T9"].iloc[1:]        # index 1, 3, 4 left
    got = rows(hours_entries(options, PROFILE, [1, 2, 3]))
    assert sorted(got) == [(1, 0, 5.0), (1, 2, 4.0), (2, 0, 3.0), (2, 1, 5.0), (3, 1, 3.0)]
