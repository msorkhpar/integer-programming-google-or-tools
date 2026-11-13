from verdict import hint_verdict

NOISE = ["Running HiGHS 1.x", "Presolving model", "Solving report"]


def test_highs_accepts_or_rejects_a_complete_hint():
    assert hint_verdict("HIGHS", NOISE + ["MIP start solution is feasible, objective value is 512"]) == "accepted"
    assert hint_verdict("HIGHS", NOISE + ["User-supplied values of discrete variables cannot yield feasible solution"]) == "rejected"


def test_cp_sat_reports_all_three_kinds():
    assert hint_verdict("CP_SAT", ["The solution hint is complete and is feasible."]) == "accepted"
    assert hint_verdict("CP_SAT", ["The solution hint is incomplete: 4 out of 30 non fixed variables hinted."]) == "partial"
    assert hint_verdict("CP_SAT", ["The solution hint is complete, but it is infeasible! we will try to repair it."]) == "repairing"


def test_a_highs_partial_hint_is_partial_even_when_completed():
    log = ["Attempting to find feasible solution by solving MIP for user-supplied values of 3 / 12 discrete variables",
           "MIP start solution is feasible, objective value is 512"]
    assert hint_verdict("HIGHS", NOISE + log) == "partial"


def test_silence_is_unknown():
    assert hint_verdict("GSCIP", NOISE) == "unknown"
    assert hint_verdict("GSCIP", ["1/1 feasible solution given by solution candidate storage, new primal bound 5.1e+02"]) == "accepted"
