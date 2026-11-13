from renovations import Renovation, forcing_cost

BRANCHES = [
    Renovation("central_roof", 40, 62),
    Renovation("east_hvac", 30, 41),
    Renovation("north_lights", 20, 23),
    Renovation("west_windows", 50, 66),
    Renovation("south_atrium", 70, 88),
    Renovation("ramp_access", 15, 4, mandatory=True),
]
BUDGET = 115      # best plan: ramp_access, east_hvac, north_lights, west_windows, worth 134


def test_forcing_a_left_out_renovation_in():
    assert forcing_cost(BRANCHES, BUDGET, "central_roof") == {
        "action": "in", "cost": 2, "dropped": ["east_hvac", "north_lights"], "added": ["central_roof"]}


def test_a_chosen_renovation_is_forced_out():
    assert forcing_cost(BRANCHES, BUDGET, "west_windows") == {
        "action": "out", "cost": 1, "dropped": ["north_lights", "west_windows"], "added": ["south_atrium"]}


def test_forcing_out_a_mandatory_renovation_has_no_cost():
    assert forcing_cost(BRANCHES, BUDGET, "ramp_access") == {
        "action": "out", "cost": None, "dropped": [], "added": []}


def test_forcing_in_a_renovation_bigger_than_the_budget_has_no_cost():
    branches = BRANCHES + [Renovation("new_wing", 120, 500)]
    assert forcing_cost(branches, BUDGET, "new_wing") == {
        "action": "in", "cost": None, "dropped": [], "added": []}
