from log_sizes import variables_before_and_after

# Made-up logs of a warehouse-slotting model, shaped like CP-SAT 9.15's.
HEADER = "Starting CP-SAT solver v9.15.6755\nParameters: log_search_progress: true num_workers: 1\n\n"


def log(before: str, after: str) -> str:
    return (HEADER
            + "Initial optimization model '': (model_fingerprint: 0xabc)\n"
            + f"#Variables: {before} (#bools: 40 in objective) (40 primary variables)\n"
            + "  - 40 Booleans in [0,1]\n#kLinear2: 18\n\nStarting presolve at 0.00s\n"
            + "[SAT presolve] [0s] clauses:23 literals:55 vars:38\n\nPresolve summary:\n"
            + "  - rule 'linear: always true' was applied 3 times.\n\n"
            + "Presolved optimization model '': (model_fingerprint: 0xdef)\n"
            + f"#Variables: {after} (#bools: 30 in objective) (30 primary variables)\n"
            + "  - 30 Booleans in [0,1]\n#kAtMostOne: 5 (#literals: 14)\n\nPreloading model.\n")


def test_presolve_that_removes_variables_is_read_before_and_after():
    assert variables_before_and_after(log("120", "97")) == (120, 97)


def test_presolve_that_removes_nothing_gives_equal_counts():
    assert variables_before_and_after(log("64", "64")) == (64, 64)


def test_counts_with_a_thousands_separator_are_read_whole():
    assert variables_before_and_after(log("12'480", "9'317")) == (12480, 9317)
