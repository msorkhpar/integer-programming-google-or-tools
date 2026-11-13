import copy

from checks import precheck

BUDGET = {2027: 1000, 2028: 1200, 2029: 900}
ENGINEERS = {2027: 30, 2028: 20, 2029: 25}
MINIMUM = {"radiology": 700, "surgery": 300}


def item(dept, cost, release, deadline, required, days, excludes=None):
    return {"dept": dept, "cost": cost, "release": release, "deadline": deadline, "required": required,
            "engineer_days": days, "excludes": excludes}


ITEMS = {
    "CT-1": item("radiology", 800, 2027, 2028, True, 10),
    "CT-2": item("radiology", 750, 2028, 2029, False, 10, excludes="XR-4"),
    "XR-4": item("radiology", 300, 2027, 2029, False, 5),
    "OR-LIGHTS": item("surgery", 400, 2028, 2028, True, 8),
    "OR-TABLES": item("surgery", 350, 2027, 2029, False, 6),
}


def edited(**changes):
    items = copy.deepcopy(ITEMS)
    for name, fields in changes.items():
        items[name] = {**items.get(name, {}), **fields}
    return items


def test_clean_data_passes_and_each_planted_cause_is_named():
    assert precheck(ITEMS, BUDGET, ENGINEERS, MINIMUM) == []
    assert precheck(edited(**{"CT-1": {"deadline": 2026}}), BUDGET, ENGINEERS, MINIMUM) == [("window", "CT-1")]
    assert precheck(edited(**{"OR-LIGHTS": {"cost": 4000}}), BUDGET, ENGINEERS, MINIMUM) == [("budget", "OR-LIGHTS")]
    assert precheck(edited(**{"OR-LIGHTS": {"engineer_days": 21}}), BUDGET, ENGINEERS, MINIMUM) == [("engineers", "OR-LIGHTS")]
    both = edited(**{"CT-2": {"required": True}, "XR-4": {"required": True}})
    assert precheck(both, BUDGET, ENGINEERS, MINIMUM) == [("exclusion", "CT-2|XR-4")]
    assert precheck(ITEMS, BUDGET, ENGINEERS, {**MINIMUM, "surgery": 800}) == [("minimum", "surgery")]


def test_a_window_entirely_outside_the_plan_years_is_caught():
    assert precheck(edited(**{"CT-1": {"release": 2030, "deadline": 2031}}), BUDGET, ENGINEERS, MINIMUM) == [("window", "CT-1")]


def test_an_item_that_fits_in_only_one_of_its_years_is_not_refused():
    fits_late = edited(**{"CT-1": {"cost": 1100}})            # too dear for 2027, fine in 2028
    assert precheck(fits_late, BUDGET, ENGINEERS, MINIMUM) == []
    assert precheck(edited(**{"CT-1": {"cost": 1300}}), BUDGET, ENGINEERS, MINIMUM) == [("budget", "CT-1")]


def test_an_exclusion_matters_only_when_both_items_are_required():
    one_required = edited(**{"XR-4": {"required": True}})     # CT-2, which excludes it, stays optional
    assert precheck(one_required, BUDGET, ENGINEERS, MINIMUM) == []
    both = edited(**{"XR-4": {"required": True}, "CT-2": {"required": True}})
    assert precheck(both, BUDGET, ENGINEERS, MINIMUM) == [("exclusion", "CT-2|XR-4")]


def test_a_department_minimum_counts_optional_items_too():
    # Surgery's required item costs 400; with the optional tables it can reach 750.
    assert precheck(ITEMS, BUDGET, ENGINEERS, {**MINIMUM, "surgery": 700}) == []
    assert precheck(ITEMS, BUDGET, ENGINEERS, {**MINIMUM, "surgery": 760}) == [("minimum", "surgery")]
