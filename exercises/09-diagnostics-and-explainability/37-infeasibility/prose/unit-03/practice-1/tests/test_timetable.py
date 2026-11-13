from timetable import conflict_among


def oracle(*clashes):
    """Infeasible exactly when the rules switched on contain one of the clashes."""
    sets = [set(c) for c in clashes]
    return lambda on: any(c <= set(on) for c in sets)


SOFT = ["7A_mornings", "7A_lab_tue", "lab_closed_tue", "8B_lab_tue"]
HARD = ["one_class_per_room", "teacher_max_6"]


def test_the_soft_rules_of_a_conflict_are_returned_and_a_feasible_timetable_gives_none():
    assert conflict_among(SOFT, HARD, oracle(["7A_lab_tue", "lab_closed_tue"])) == ["7A_lab_tue", "lab_closed_tue"]
    assert conflict_among(SOFT, HARD, oracle(["7A_mornings", "unknown_rule"])) is None


def test_a_hard_rule_takes_part_in_every_question():
    # Two classes in the lab on Tuesday clash only because a room holds one class: a hard rule.
    clash = oracle(["7A_lab_tue", "8B_lab_tue", "one_class_per_room"])
    assert conflict_among(SOFT, HARD, clash) == ["7A_lab_tue", "8B_lab_tue"]


def test_a_rule_once_dropped_stays_dropped():
    # Two separate conflicts: the filter must end with exactly one of them.
    clash = oracle(["7A_mornings", "7A_lab_tue"], ["lab_closed_tue", "8B_lab_tue"])
    assert conflict_among(SOFT, HARD, clash) == ["lab_closed_tue", "8B_lab_tue"]

