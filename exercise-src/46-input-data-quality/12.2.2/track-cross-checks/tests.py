import copy

from cross import cross_checks

# A rail operator's track-renewal snapshot. Crews are crew-weeks available over the whole horizon.
CLEAN = {
    "crews": {"track": 12, "signals": 8},
    "jobs": [
        {"id": "T1", "crew": "track", "crew_weeks": 5, "required": True, "after": None, "exclusive": None},
        {"id": "T2", "crew": "track", "crew_weeks": 4, "required": False, "after": None, "exclusive": "G1"},
        {"id": "T3", "crew": "track", "crew_weeks": 2, "required": False, "after": None, "exclusive": "G1"},
        {"id": "S1", "crew": "signals", "crew_weeks": 1, "required": False, "after": "T2", "exclusive": None},
        {"id": "S2", "crew": "signals", "crew_weeks": 5, "required": True, "after": None, "exclusive": "G2"},
        {"id": "S3", "crew": "signals", "crew_weeks": 2, "required": False, "after": None, "exclusive": "G2"},
    ],
}


def edited(**changes) -> dict:
    """CLEAN with some jobs' fields replaced: edited(T2={"required": True})."""
    doc = copy.deepcopy(CLEAN)
    for job in doc["jobs"]:
        job.update(changes.get(job["id"], {}))
    return doc


def test_a_clean_snapshot_passes_and_two_required_alternatives_are_found():
    assert cross_checks(CLEAN) == []
    assert cross_checks(edited(T2={"required": True}, T3={"required": True})) == [("exclusive-required", "G1")]


def test_a_prerequisite_of_a_required_job_counts_as_required():
    # S1 needs T2, so making S1 and T3 required makes T2 and T3 both required in group G1.
    assert cross_checks(edited(S1={"required": True}, T3={"required": True})) == [("exclusive-required", "G1")]


def test_optional_jobs_never_trigger_a_rule():
    assert cross_checks(edited(S3={"crew_weeks": 7})) == []


def test_a_group_is_reported_once():
    doc = edited(T2={"required": True}, T3={"required": True})
    doc["jobs"].append({"id": "T4", "crew": "track", "crew_weeks": 0, "required": True, "after": None,
                        "exclusive": "G1"})
    assert cross_checks(doc) == [("exclusive-required", "G1")]


def test_required_crew_weeks_above_the_supply_are_found_and_equal_to_it_pass():
    assert cross_checks(edited(S2={"crew_weeks": 8})) == []
    assert cross_checks(edited(S2={"crew_weeks": 9})) == [("crew-short", "signals")]


def test_a_prerequisite_uses_its_own_crew():
    # S1 (signals) needs T2 (track): required track work becomes 9 + 4 = 13 > 12.
    assert cross_checks(edited(S1={"required": True}, T2={"crew_weeks": 4}, T1={"crew_weeks": 9})) == \
        [("crew-short", "track")]
