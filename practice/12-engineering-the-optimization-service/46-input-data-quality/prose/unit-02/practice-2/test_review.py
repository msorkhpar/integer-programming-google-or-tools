import copy

from review import rejected, review

# A water utility's main-replacement snapshot (money in $k), already valid against its schema.
CLEAN = {
    "horizon": [2027, 2028, 2029, 2030],
    "budgets": {2027: 1000, 2028: 1000, 2029: 1000, 2030: 1000},
    "jobs": [
        {"id": "M1", "cost": [600], "earliest": 2027, "latest": 2028, "required": True, "after": None, "lag": 0},
        {"id": "M2", "cost": [300, 300], "earliest": 2027, "latest": 2029, "required": False, "after": None, "lag": 0},
        {"id": "M3", "cost": [400], "earliest": 2028, "latest": 2030, "required": False, "after": "M2", "lag": 1},
        {"id": "M4", "cost": [200], "earliest": 2027, "latest": 2030, "required": False, "after": None, "lag": 0},
        {"id": "M5", "cost": [500], "earliest": 2029, "latest": 2030, "required": False, "after": "M4", "lag": 0},
        {"id": "M6", "cost": [250, 250], "earliest": 2028, "latest": 2029, "required": True, "after": "M1", "lag": 1},
    ],
}


def edited(jobs: dict | None = None, add: list | None = None, budgets: dict | None = None) -> dict:
    """CLEAN with some jobs' fields replaced, some jobs added, some budgets replaced."""
    doc = copy.deepcopy(CLEAN)
    for job in doc["jobs"]:
        job.update((jobs or {}).get(job["id"], {}))
    doc["jobs"] += add or []
    doc["budgets"].update(budgets or {})
    return doc


M7_LATE = {"id": "M7", "cost": [100], "earliest": 2031, "latest": 2032, "required": True, "after": None, "lag": 0}
M8_TYPO = {"id": "M8", "cost": [2500], "earliest": 2027, "latest": 2030, "required": True, "after": "M2", "lag": 0}

# The export with six planted defects: a cycle M4 <-> M5, M6's lag typed 3, M3's lag typed 4,
# a required M7 dated after the horizon, M8's cost typed 2500 for 250, and 2030's budget typed 300.
DIRTY = edited(jobs={"M4": {"after": "M5", "lag": 1}, "M6": {"lag": 3}, "M3": {"lag": 4}},
               add=[M7_LATE, M8_TYPO], budgets={2030: 300})


def test_a_clean_snapshot_passes_and_the_six_defects_are_all_found():
    assert review(CLEAN, CLEAN) == [] and not rejected(review(CLEAN, CLEAN))
    findings = review(DIRTY, CLEAN)
    assert rejected(findings)
    assert {(rule, subject) for _, rule, subject in findings} >= {
        ("prerequisite-cycle", "M4+M5"), ("prerequisite-too-late", "M6"), ("prerequisite-too-late", "M3"),
        ("no-start-in-horizon", "M7"), ("required-over-budget", "plan"), ("budget-drift", "2030")}


def test_a_cycle_is_reported_once():
    assert review(edited(jobs={"M4": {"after": "M5", "lag": 1}}), CLEAN) == [
        ("error", "prerequisite-cycle", "M4+M5")]


def test_a_required_job_whose_prerequisite_is_too_late_is_an_error():
    assert review(edited(jobs={"M6": {"lag": 3}}), CLEAN) == [("error", "prerequisite-too-late", "M6")]


def test_an_optional_job_whose_prerequisite_is_too_late_is_a_warning():
    assert review(edited(jobs={"M3": {"lag": 4}}), CLEAN) == [("warning", "prerequisite-too-late", "M3")]


def test_a_prerequisite_of_a_required_job_is_held_to_the_error_rule():
    # M3 is now required, so its optional prerequisite M2 must be done too; M2 waits on M4 with a
    # lag of 3, and M4's earliest start plus 3 is after M2's last start.
    doc = edited(jobs={"M3": {"required": True}, "M2": {"after": "M4", "lag": 3}})
    assert review(doc, CLEAN) == [("error", "prerequisite-too-late", "M2")]


def test_a_start_needs_room_for_every_year_of_work():
    m7 = {"id": "M7", "cost": [100, 100, 100], "earliest": 2029, "latest": 2030, "required": True,
          "after": None, "lag": 0}
    assert review(edited(add=[m7]), CLEAN) == [("error", "no-start-in-horizon", "M7")]


def test_a_prerequisite_of_a_required_job_counts_toward_required_spend():
    doc = edited(jobs={"M3": {"required": True}}, budgets={y: 500 for y in CLEAN["horizon"]})
    assert review(doc, CLEAN) == [("error", "required-over-budget", "plan")]


def test_drift_is_flagged_both_ways_but_not_for_an_ordinary_cut():
    doc = edited(budgets={2028: 700, 2029: 3500, 2030: 300})
    assert review(doc, CLEAN) == [("warning", "budget-drift", "2029"), ("warning", "budget-drift", "2030")]
