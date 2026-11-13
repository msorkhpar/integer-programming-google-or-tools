import copy

from export import rejected, review

# A fictional utility's practice export: every cell is text, as csv.DictReader gives it. Money in $k.
COLUMNS = ("id", "program", "region", "cost", "earliest", "latest", "must", "parent", "lag", "group", "crews")
ROWS = [
    ("J1", "lines", "North", "200;100", "2027", "2028", "1", "", "0", "", "2"),
    ("J2", "poles", "South", "120", "2027", "2029", "0", "", "0", "", "1"),
    ("J3", "lines", "North", "150", "2028", "2029", "0", "J1", "1", "", "2"),
    ("J4", "poles", "South", "80;80", "2027", "2028", "0", "", "0", "G1", "1"),
    ("J5", "poles", "South", "60", "2027", "2029", "0", "", "0", "G1", "1"),
    ("J6", "lines", "North", "90", "2028", "2029", "1", "", "0", "", "1"),
]
CLEAN = {
    "years": [2027, 2028, 2029], "rate": "0.05",
    "budgets": [{"year": str(y), "amount": "400"} for y in (2027, 2028, 2029)],
    "projects": [dict(zip(COLUMNS, row)) for row in ROWS],
}


def edited(cells: dict | None = None, budgets: dict | None = None) -> dict:
    """CLEAN with some cells replaced: cells = {project id: {column: text}}, budgets = {year: text}."""
    doc = copy.deepcopy(CLEAN)
    for row in doc["projects"]:
        row.update((cells or {}).get(row["id"], {}))
    for row in doc["budgets"]:
        row["amount"] = (budgets or {}).get(int(row["year"]), row["amount"])
    return doc


CELL_DEFECTS = {"J2": {"cost": "12O"}, "J3": {"region": "Nroth"}, "J4": {"earliest": "2029", "latest": "2028"},
                "J5": {"parent": "J9"}}
CROSS_DEFECTS = {"J1": {"parent": "J6"}, "J6": {"parent": "J1"}}


def test_a_clean_export_is_accepted_as_the_snapshot():
    snap, findings = review(CLEAN)
    assert findings == [] and not rejected(findings) and snap is not None
    assert snap["years"] == [2027, 2028, 2029] and snap["rate"] == 0.05
    assert snap["budget"] == {2027: 400, 2028: 400, 2029: 400}
    assert snap["projects"]["J1"] == {"program": "lines", "region": "North", "cost": [200, 100], "earliest": 2027,
                                      "latest": 2028, "must": True, "parent": None, "lag": 0, "group": None,
                                      "crews": 2}
    assert snap["projects"]["J3"]["parent"] == "J1" and snap["projects"]["J4"]["group"] == "G1"
    assert sorted(snap["projects"]) == ["J1", "J2", "J3", "J4", "J5", "J6"]


def test_six_planted_defects_are_found_in_two_passes():
    snap, first = review(edited({**CELL_DEFECTS, **CROSS_DEFECTS}, {2028: "40"}))
    assert snap is None and rejected(first)
    assert first == [("error", "empty-window", "J4"), ("error", "not-a-number", "J2.cost"),
                     ("error", "unknown-code", "J3.region"), ("error", "unknown-parent", "J5")]
    snap, second = review(edited(CROSS_DEFECTS, {2028: "40"}))
    assert snap is None and rejected(second)
    assert {(rule, subject) for _, rule, subject in second} == {("must-spend-over-budget", "2028"),
                                                               ("parent-cycle", "J1+J6")}


def test_every_problem_in_a_row_is_kept():
    snap, findings = review(edited({"J2": {"cost": "12O", "region": "Sout"}}))
    assert snap is None
    assert findings == [("error", "not-a-number", "J2.cost"), ("error", "unknown-code", "J2.region")]


def test_every_year_of_a_cost_profile_is_read():
    snap, findings = review(edited({"J4": {"cost": "80;8,0"}}))
    assert snap is None and findings == [("error", "not-a-number", "J4.cost")]


def test_the_window_leaves_room_for_every_year_of_work():
    snap, findings = review(edited({"J2": {"cost": "120;120"}}))
    assert snap is None and findings == [("error", "empty-window", "J2")]


def test_a_cycle_is_one_finding():
    snap, findings = review(edited(CROSS_DEFECTS))
    assert snap is None and findings == [("error", "parent-cycle", "J1+J6")]


def test_a_parent_too_late_for_an_optional_child_only_warns():
    snap, findings = review(edited({"J3": {"lag": "3"}}))
    assert findings == [("warning", "parent-too-late", "J3")]
    assert not rejected(findings) and snap is not None and snap["projects"]["J3"]["lag"] == 3


def test_a_parent_too_late_for_a_must_do_child_blocks():
    snap, findings = review(edited({"J6": {"parent": "J1", "lag": "3"}}))
    assert snap is None and findings == [("error", "parent-too-late", "J6")]


def test_must_do_spend_counts_each_must_dos_cheapest_start():
    snap, findings = review(edited(budgets={2027: "150"}))
    assert findings == [] and snap is not None and snap["budget"][2027] == 150


def test_a_budget_row_with_a_bad_year_is_named_by_its_text_and_leaves_its_year_missing():
    doc = edited()
    doc["budgets"][1]["year"] = "2O28"
    snap, findings = review(doc)
    assert snap is None and findings == [("error", "bad-budget", "2O28"), ("error", "missing-budget", "2028")]


def test_a_window_is_checked_even_when_a_cost_amount_is_bad():
    snap, findings = review(edited({"J2": {"cost": "120;12O"}}))
    assert snap is None and findings == [("error", "empty-window", "J2"), ("error", "not-a-number", "J2.cost")]


def test_a_cost_cell_with_two_bad_amounts_is_one_finding():
    snap, findings = review(edited({"J4": {"cost": "8O;8,0"}}))
    assert snap is None and findings == [("error", "not-a-number", "J4.cost")]
