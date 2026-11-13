from outages import Outage, violations


def rules(found):
    return sorted({line.split(":")[0] for line in found})


GOOD = [Outage("O1", "Elm", 10, 3, 2), Outage("O2", "Elm", 14, 2, 1), Outage("O3", "Oak", 11, 4, 2)]


def test_a_sound_schedule_passes_and_a_broken_one_names_its_rules():
    assert violations(GOOD, crews_per_week=4) == []
    bad = [Outage("O1", "Elm", 10, 3, 2), Outage("O2", "Elm", 11, 2, 1), Outage("O1", "Oak", 51, 3, 2)]
    assert rules(violations(bad, crews_per_week=4)) == ["inside the year", "one outage per site", "unique ids"]


def test_an_outage_ending_in_week_52_is_inside_the_year():
    assert violations([Outage("O9", "Ash", 50, 3, 1)], crews_per_week=4) == []
    assert rules(violations([Outage("O9", "Ash", 51, 3, 1)], crews_per_week=4)) == ["inside the year"]


def test_back_to_back_outages_at_one_site_do_not_overlap():
    assert violations([Outage("O1", "Elm", 10, 3, 1), Outage("O2", "Elm", 13, 1, 1)], crews_per_week=4) == []
    found = violations([Outage("O1", "Elm", 10, 3, 1), Outage("O2", "Elm", 12, 1, 1)], crews_per_week=4)
    assert rules(found) == ["one outage per site"]


def test_crews_count_in_every_week_of_an_outage():
    assert violations([Outage("O1", "Elm", 10, 3, 3), Outage("O2", "Oak", 13, 2, 3)], crews_per_week=3) == []
    found = violations([Outage("O1", "Elm", 10, 3, 3), Outage("O2", "Oak", 12, 2, 2)], crews_per_week=4)
    assert found == ["crews suffice: week 12 needs 5"]


def test_each_duplicated_id_is_reported_once():
    plan = [Outage("O1", "Elm", 1, 1, 1), Outage("O1", "Oak", 5, 1, 1), Outage("O1", "Ash", 9, 1, 1)]
    assert violations(plan, crews_per_week=4) == ["unique ids: O1"]
    assert violations(plan[:1], crews_per_week=4) == []


def test_lines_keep_the_stated_order_and_ids_compare_as_strings():
    plan = [Outage("O2", "Elm", 10, 3, 1), Outage("O10", "Elm", 11, 2, 1), Outage("O2", "Oak", 51, 3, 5)]
    assert violations(plan, crews_per_week=4) == [
        "unique ids: O2",
        "inside the year: O2",
        "one outage per site: O10 and O2",
        "crews suffice: week 51 needs 5",
        "crews suffice: week 52 needs 5",
        "crews suffice: week 53 needs 5",
    ]


def test_crews_count_in_weeks_past_the_year():
    found = violations([Outage("O1", "Elm", 51, 3, 5)], crews_per_week=4)
    assert found == ["inside the year: O1", "crews suffice: week 51 needs 5",
                     "crews suffice: week 52 needs 5", "crews suffice: week 53 needs 5"]
