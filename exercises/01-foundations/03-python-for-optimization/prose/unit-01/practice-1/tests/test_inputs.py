import io

import pandas as pd

from inputs import model_inputs

# A feeder program unlike the lesson's portfolio. Money in $k. Frames are read with pandas'
# defaults, exactly as a loader that passes no dtype= would read them.


def frame(text: str) -> pd.DataFrame:
    return pd.read_csv(io.StringIO(text))


FEEDERS = frame("""project_id,cost_profile,earliest_start,parent
F1,300;200,2030,
F2,450,2030,F1
F3,120;80;40,2031,
F4,90,2030,F1
""")

NPV_SORTED = frame("""project_id,start_year,npv
F1,2030,520
F1,2031,410
F2,2030,300
F3,2031,150
F3,2032,90
F4,2030,60
""")


def test_capex_sums_each_profile():
    capex, _, _ = model_inputs(FEEDERS, NPV_SORTED)
    assert capex == {"F1": 500, "F2": 450, "F3": 240, "F4": 90}


def test_value_is_the_npv_at_the_earliest_start():
    _, value, _ = model_inputs(FEEDERS, NPV_SORTED)
    assert value == {"F1": 520, "F2": 300, "F3": 150, "F4": 60}


def test_a_file_of_one_year_profiles_still_works():
    short = frame("""project_id,cost_profile,earliest_start,parent
S1,75,2030,
S2,40,2031,S1
""")
    npv = frame("""project_id,start_year,npv
S1,2030,90
S2,2031,55
""")
    try:
        capex, _, _ = model_inputs(short, npv)
    except AttributeError as error:  # a text method called on a column pandas read as integers
        capex = f"raised AttributeError: {error}"
    assert capex == {"S1": 75, "S2": 40}


def test_npv_rows_may_come_in_any_order():
    shuffled = frame("""project_id,start_year,npv
F3,2032,90
F1,2031,410
F4,2030,60
F2,2030,300
F1,2030,520
F3,2031,150
""")
    _, value, _ = model_inputs(FEEDERS, shuffled)
    assert value == {"F1": 520, "F2": 300, "F3": 150, "F4": 60}


def test_a_later_start_worth_more_is_not_the_value():
    later_better = frame("""project_id,start_year,npv
F1,2030,520
F1,2031,410
F2,2030,300
F3,2031,150
F3,2032,170
F4,2030,60
""")
    _, value, _ = model_inputs(FEEDERS, later_better)
    assert value.get("F3") == 150


def test_only_children_have_a_parent():
    _, _, parent = model_inputs(FEEDERS, NPV_SORTED)
    assert parent == {"F2": "F1", "F4": "F1"}
