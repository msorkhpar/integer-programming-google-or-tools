from messages import translate

JOBS = {"R12": "Elm Street", "R31": "Harbour Road", "R07": "Mill Lane"}
CAPS = {2027: 12500, 2028: 9800, 2029: 950}
CREWS = {("north", 2027): 3, ("south_east", 2028): 2, ("west", 2029): 1}


def test_each_kind_of_row_becomes_its_sentence():
    conflict = ["need_R12", "pin_R31_2027", "cap_2029", "before_R07_R12"]
    assert translate(conflict, JOBS, CAPS, CREWS) == [
        "R12 Elm Street must be done this plan.",
        "Council fixed R31 Harbour Road to 2027.",
        "The 2029 resurfacing budget is $950k.",
        "R07 Mill Lane must finish before R12 Elm Street starts.",
    ]


def test_a_district_name_may_contain_an_underscore():
    assert translate(["crew_south_east_2028", "crew_north_2027"], JOBS, CAPS, CREWS) == [
        "The south east district has 2 paving crews in 2028.",
        "The north district has 3 paving crews in 2027.",
    ]


def test_money_is_written_with_a_thousands_separator():
    assert translate(["cap_2028"], JOBS, CAPS, CREWS) == ["The 2028 resurfacing budget is $9,800k."]


def test_a_row_the_translator_does_not_know_still_gets_a_sentence():
    assert translate(["noise_R12_night"], JOBS, CAPS, CREWS) == ["Rule noise_R12_night has no description yet."]


def test_a_row_naming_an_unknown_job_or_district_gets_the_same_fallback():
    assert translate(["need_R99", "crew_east_2027", "cap_2031", "pin_R31_2027"], JOBS, CAPS, CREWS) == [
        "Rule need_R99 has no description yet.",
        "Rule crew_east_2027 has no description yet.",
        "Rule cap_2031 has no description yet.",
        "Council fixed R31 Harbour Road to 2027.",
    ]


def test_one_crew_is_singular():
    assert translate(["crew_west_2029"], JOBS, CAPS, CREWS) == ["The west district has 1 paving crew in 2029."]
