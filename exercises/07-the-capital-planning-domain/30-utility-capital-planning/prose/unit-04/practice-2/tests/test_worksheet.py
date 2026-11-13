from worksheet import by_stakeholder, trace

# A water utility's worksheet. Not the lesson's.


def req(rid, who):
    return {"id": rid, "stakeholder": who, "text": f"requirement {rid}"}


def test_each_requirement_gets_a_status():
    reqs = [req("Q1", "finance"), req("Q2", "finance"), req("Q3", "planner")]
    checks = [{"name": "spend", "covers": ["Q1"], "passed": True},
              {"name": "npv", "covers": ["Q2"], "passed": False}]
    assert trace(reqs, checks) == {"Q1": "MET", "Q2": "FAILED", "Q3": "UNTESTED"}


def test_counts_by_stakeholder():
    reqs = [req("Q1", "finance"), req("Q2", "finance"), req("Q3", "finance"),
            req("Q4", "auditor"), req("Q5", "auditor"), req("Q6", "auditor"), req("Q7", "auditor")]
    status = {"Q1": "MET", "Q2": "FAILED", "Q3": "UNTESTED",
              "Q4": "MET", "Q5": "MET", "Q6": "FAILED", "Q7": "UNTESTED"}
    assert by_stakeholder(reqs, status) == {
        "finance": {"MET": 1, "FAILED": 1, "UNTESTED": 1}, "auditor": {"MET": 2, "FAILED": 1, "UNTESTED": 1}}


def test_one_failing_check_fails_the_requirement():
    reqs = [req("Q1", "auditor"), req("Q2", "auditor")]
    checks = [{"name": "rerun", "covers": ["Q1"], "passed": True},
              {"name": "rerun_8_threads", "covers": ["Q1"], "passed": False},
              {"name": "floors", "covers": ["Q2"], "passed": True}]
    assert trace(reqs, checks) == {"Q1": "FAILED", "Q2": "MET"}


def test_every_state_is_counted_even_at_zero():
    reqs = [req("Q1", "planner"), req("Q2", "finance")]
    assert by_stakeholder(reqs, {"Q1": "MET", "Q2": "UNTESTED"}) == {
        "planner": {"MET": 1, "FAILED": 0, "UNTESTED": 0}, "finance": {"MET": 0, "FAILED": 0, "UNTESTED": 1}}


def test_a_check_counts_for_every_requirement_it_covers():
    reqs = [req("Q1", "finance"), req("Q2", "finance"), req("Q3", "planner")]
    checks = [{"name": "budget_rows", "covers": ["Q1", "Q2"], "passed": False},
              {"name": "windows", "covers": ["Q3"], "passed": True}]
    assert trace(reqs, checks) == {"Q1": "FAILED", "Q2": "FAILED", "Q3": "MET"}
