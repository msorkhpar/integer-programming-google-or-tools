from hospital_audit import audit_failures

ITEMS = {
    "mri_2": {"years": [2028, 2029], "cost": 2400, "mandatory": False},
    "ct_1": {"years": [2027, 2028], "cost": 1300, "mandatory": False},
    "sterilizer": {"years": [2027], "cost": 400, "mandatory": True},
    "beds_west": {"years": [2027, 2028, 2029], "cost": 900, "mandatory": False},
    "xray_3": {"years": [2028, 2029], "cost": 700, "mandatory": False},
}
BUDGET = {2027: 2000, 2028: 3000, 2029: 1600}
GROUPS = {"imaging": ["mri_2", "ct_1"]}


def failures(plan):
    return audit_failures(plan, ITEMS, BUDGET, GROUPS)


def test_a_clean_plan_passes_and_an_overspent_year_fails():
    assert failures({"sterilizer": 2027, "ct_1": 2027, "beds_west": 2028, "xray_3": 2028}) == []
    assert failures({"sterilizer": 2027, "mri_2": 2028, "beds_west": 2028}) == ["budget 2028"]


def test_a_purchase_before_its_window_fails():
    assert failures({"sterilizer": 2027, "xray_3": 2029}) == []
    assert failures({"sterilizer": 2027, "xray_3": 2027}) == ["window xray_3"]


def test_a_missing_mandatory_purchase_fails():
    assert failures({"sterilizer": 2027, "ct_1": 2027}) == []
    assert failures({"ct_1": 2027}) == ["mandatory sterilizer"]


def test_two_options_of_one_group_fail_even_in_different_years():
    assert failures({"sterilizer": 2027, "mri_2": 2028}) == []
    assert failures({"sterilizer": 2027, "ct_1": 2027, "mri_2": 2028}) == ["exclusive imaging"]


def test_a_year_spent_exactly_to_its_budget_passes():
    assert failures({"sterilizer": 2027, "xray_3": 2029, "beds_west": 2029}) == []
    assert failures({"sterilizer": 2027, "mri_2": 2029}) == ["budget 2029"]
