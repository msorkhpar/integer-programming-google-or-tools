from district import least_overspend

PROJECTS = {
    "roof-A": {2027: 300},
    "boiler-B": {2027: 200, 2028: 250},
    "windows-C": {2028: 400},
    "gym-D": {2027: 500, 2028: 500},
}


def test_a_feasible_plan_needs_no_overspend_and_a_tight_one_needs_the_difference():
    pair = {name: PROJECTS[name] for name in ("roof-A", "boiler-B")}
    assert least_overspend(pair, {2027: 600}, {"roof-A", "boiler-B"}) == {2027: 0}
    assert least_overspend(pair, {2027: 450}, {"roof-A", "boiler-B"}) == {2027: 50}


def test_each_year_overspends_only_by_its_own_shortfall():
    assert least_overspend(PROJECTS, {2027: 450, 2028: 700}, {"roof-A", "boiler-B", "windows-C"}) == {2027: 50, 2028: 0}


def test_money_left_in_one_year_does_not_pay_for_another():
    assert least_overspend(PROJECTS, {2027: 800, 2028: 500}, {"roof-A", "boiler-B", "windows-C"}) == {2027: 0, 2028: 150}


def test_optional_projects_never_add_to_the_overspend():
    assert least_overspend(PROJECTS, {2027: 400, 2028: 300}, {"roof-A", "boiler-B"}) == {2027: 100, 2028: 0}
