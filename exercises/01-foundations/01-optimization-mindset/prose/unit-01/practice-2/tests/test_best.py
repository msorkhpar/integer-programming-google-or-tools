from best import Project, best_plan

FEEDERS = [
    Project("F1", 120, 150),
    Project("F2", 200, 290, must_do=True),
    Project("F3", 90, 140),
    Project("F4", 60, 95, parent="F3"),
    Project("F5", 150, 230, group="tap"),
    Project("F6", 40, 70, group="tap"),
    Project("F7", 30, 20),
]


def breaks_a_feeder_rule(plan) -> bool:
    """The rules of FEEDERS at budget 600, spelled out for this one portfolio."""
    cost = sum(p.cost for p in FEEDERS if p.pid in plan)
    return (cost > 600 or "F2" not in plan or ("F4" in plan and "F3" not in plan)
            or {"F5", "F6"} <= set(plan))


def test_the_plan_returned_is_allowed_and_valued_correctly():
    result = best_plan(FEEDERS, 600)
    assert result is not None
    value, plan = result
    assert not breaks_a_feeder_rule(plan)
    assert value == sum(p.value for p in FEEDERS if p.pid in plan)


def test_no_allowed_plan_is_worth_more():
    result = best_plan(FEEDERS, 600)
    assert result is not None and result[0] == 830
    assert best_plan(FEEDERS, 400) == (595, frozenset({"F2", "F3", "F4", "F6"}))
    # A plan with fewer projects can be worth more: R1 alone beats R2 + R3 here.
    assert best_plan([Project("R1", 100, 200), Project("R2", 50, 90), Project("R3", 50, 85)], 100) \
        == (200, frozenset({"R1"}))


def test_a_must_do_is_funded_even_when_it_loses_value():
    projects = [Project("C1", 50, -30, must_do=True), Project("C2", 40, 60), Project("C3", 70, 65)]
    assert best_plan(projects, 130) == (35, frozenset({"C1", "C3"}))


def test_ties_go_to_the_cheaper_plan():
    projects = [Project("T1", 80, 100), Project("T2", 30, 60), Project("T3", 40, 40)]
    assert best_plan(projects, 80) == (100, frozenset({"T2", "T3"}))


def test_no_allowed_plan_returns_none():
    projects = [Project("M1", 90, 100, must_do=True), Project("M2", 60, 80, must_do=True)]
    assert best_plan(projects, 120) is None
