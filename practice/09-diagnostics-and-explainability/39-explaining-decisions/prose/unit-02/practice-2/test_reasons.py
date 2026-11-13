from reasons import why_deferred

GROUPS = {"reline_M4": "main_4", "replace_M4": "main_4", "reline_M9": "main_9", "replace_M9": "main_9"}
BEST = {"replace_M4", "replace_M9", "valve_V2", "hydrant_H7"}


def test_a_deferred_option_names_its_alternative_and_what_else_gives_way():
    forced = {"reline_M4", "replace_M9", "hydrant_H7"}
    assert why_deferred("reline_M4", GROUPS, BEST, forced) == ["alternative replace_M4", "displaced valve_V2"]


def test_an_impossible_forcing_is_reported_as_infeasible():
    assert why_deferred("reline_M4", GROUPS, BEST, None) == ["infeasible"]


def test_a_forcing_that_drops_nothing_says_so():
    assert why_deferred("meter_X1", GROUPS, BEST, BEST | {"meter_X1"}) == ["nothing displaced"]


def test_a_main_without_a_group_has_no_alternatives():
    forced = {"pump_P3", "replace_M9", "hydrant_H7"}
    assert why_deferred("pump_P3", GROUPS, BEST, forced) == ["displaced replace_M4", "displaced valve_V2"]


def test_alternatives_come_before_other_projects_given_way():
    forced = {"reline_M9", "valve_V2"}
    assert why_deferred("reline_M9", GROUPS, BEST, forced) == \
        ["alternative replace_M9", "displaced hydrant_H7", "displaced replace_M4"]
