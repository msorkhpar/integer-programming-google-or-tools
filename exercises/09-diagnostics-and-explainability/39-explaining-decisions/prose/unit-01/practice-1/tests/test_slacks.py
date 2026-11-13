from slacks import Row, binding, slack

ROWS = [
    Row("depot_space", {"bus_a": 12, "bus_b": 9}, "<=", 40),        # bays used by the new buses
    Row("electric_floor", {"bus_b": 1, "bus_c": 1}, ">=", 2),       # electric buses bought
    Row("charger_contract", {"charger": 1}, "==", 1),               # the charger contract is signed
    Row("grant_cap", {"bus_a": 300, "bus_c": 450}, "<=", 1200),     # grant money used, $k
]


def test_a_plan_s_slack_and_its_binding_rows():
    plan = {"bus_a": 1, "bus_b": 2, "bus_c": 0, "charger": 1}
    assert slack(ROWS[0], plan) == 10                               # 12 + 18 = 30 of 40
    assert binding(ROWS, plan) == ["electric_floor", "charger_contract"]


def test_a_floor_row_has_room_above_its_floor():
    plan = {"bus_a": 0, "bus_b": 3, "bus_c": 2, "charger": 1}
    assert slack(ROWS[1], plan) == 3                                # 5 electric against a floor of 2
    assert binding(ROWS, plan) == ["charger_contract"]


def test_an_equality_row_missed_from_below_is_broken():
    plan = {"bus_a": 1, "bus_b": 2, "charger": 0}
    assert slack(ROWS[2], plan) == -1
    assert binding(ROWS, plan) == ["electric_floor"]


def test_a_broken_row_is_not_binding():
    plan = {"bus_a": 4, "bus_b": 2, "bus_c": 0, "charger": 1}       # 66 bays of 40; grant 1,200 of 1,200
    assert slack(ROWS[0], plan) == -26
    assert binding(ROWS, plan) == ["electric_floor", "charger_contract", "grant_cap"]


def test_a_slack_within_the_tolerance_binds():
    rows = [Row("grant_cap", {"bus_a": 0.1, "bus_c": 0.2}, "<=", 0.3)]
    plan = {"bus_a": 1, "bus_c": 1}                                 # 0.1 + 0.2 is 0.30000000000000004
    assert binding(rows, plan) == ["grant_cap"]
