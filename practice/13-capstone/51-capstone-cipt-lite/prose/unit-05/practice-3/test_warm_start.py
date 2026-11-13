import copy

from warm_start import build, carry, check, hint, plan_of, repair, solve


def job(cost, earliest, latest, npv, must=False, parent=None, lag=0):
    return {"cost": cost, "earliest": earliest, "latest": latest, "must": must, "parent": parent, "lag": lag,
            "group": None, "npv": dict(zip(range(earliest, latest + 1), npv))}


# This cycle's practice portfolio: finance cut every year to $300k.
SNAPSHOT = {"years": [2027, 2028, 2029], "budget": {2027: 300, 2028: 300, 2029: 300}, "projects": {
    "J1": job([100], 2027, 2028, [40, 35], must=True),
    "J2": job([150], 2027, 2029, [60, 55, 50]),
    "J3": job([100, 100], 2027, 2028, [70, 65]),
    "J4": job([100], 2028, 2029, [20, 18]),
    "J5": job([50], 2028, 2029, [30, 28], parent="J2", lag=1),
    "J6": job([100], 2027, 2027, [25]),
}}
# Last cycle's plan: J9 is retired, and the rest overspends 2027 under this cycle's budget.
LAST = {"J1": 2027, "J2": 2027, "J3": 2027, "J4": 2028, "J5": 2028, "J6": 2027, "J9": 2028}


def edited(**npv):
    snap = copy.deepcopy(SNAPSHOT)
    for j, values in npv.items():
        snap["projects"][j]["npv"] = dict(zip(sorted(snap["projects"][j]["npv"]), values))
    return snap


def test_carry_keeps_only_the_starts_this_cycle_has_a_variable_for():
    assert carry(LAST, SNAPSHOT) == {"J1": 2027, "J2": 2027, "J3": 2027, "J4": 2028, "J5": 2028, "J6": 2027}
    assert carry({"J4": 2030, "J6": 2028, "J1": 2028}, SNAPSHOT) == {"J1": 2028}


def test_the_repaired_start_breaks_no_rule_and_the_hinted_solve_reaches_the_same_optimum():
    model, x = build(SNAPSHOT)
    start = repair(SNAPSHOT, carry(LAST, SNAPSHOT))
    assert start and check(SNAPSHOT, start) == []
    params = hint(x, start)
    given = params.solution_hints[0].variable_values if params.solution_hints else {}
    assert {j: t for (j, t), v in x.items() if given.get(v, 0) > 0.5} == start
    plain, hinted = solve(model), solve(model, params)
    assert hinted.termination.reason.name == "OPTIMAL"
    assert abs(hinted.objective_value() - plain.objective_value()) < 1e-6
    assert check(SNAPSHOT, plan_of(x, hinted)) == []


def test_the_hint_sets_every_variable_zeros_included():
    model, x = build(SNAPSHOT)
    params = hint(x, {"J1": 2027})
    given = params.solution_hints[0].variable_values if params.solution_hints else {}
    assert len(given) == len(x) and sorted(given.values()).count(1.0) == 1


def test_repair_drops_the_least_npv_per_dollar_first():
    assert repair(SNAPSHOT, carry(LAST, SNAPSHOT)) == {"J1": 2027, "J2": 2027, "J4": 2028, "J5": 2028}


def test_repair_drops_only_projects_that_spend_in_a_broken_year():
    start = repair(SNAPSHOT, carry(LAST, SNAPSHOT))
    assert start.get("J4") == 2028 and start.get("J5") == 2028


def test_repair_never_drops_a_must_do():
    cheap_must = edited(J1=[5, 4])
    start = repair(cheap_must, carry(LAST, cheap_must))
    assert start.get("J1") == 2027 and check(cheap_must, start) == []


def test_a_dropped_parent_takes_its_child_with_it():
    weak_parent = edited(J2=[10, 9, 8])
    start = repair(weak_parent, carry(LAST, weak_parent))
    assert "J2" not in start and "J5" not in start and check(weak_parent, start) == []


def test_carry_drops_a_child_whose_parent_has_no_start_left():
    assert carry({"J2": 2030, "J5": 2029, "J1": 2027}, SNAPSHOT) == {"J1": 2027}


def test_a_must_do_child_keeps_its_parent():
    # J5 is now a must-do and needs J2: J2 cannot be dropped, though its NPV per $k is the least.
    must_child = edited(J2=[10, 9, 8])
    must_child["projects"]["J5"]["must"] = True
    start = repair(must_child, carry(LAST, must_child))
    assert start == {"J1": 2027, "J2": 2027, "J4": 2028, "J5": 2028} and check(must_child, start) == []
