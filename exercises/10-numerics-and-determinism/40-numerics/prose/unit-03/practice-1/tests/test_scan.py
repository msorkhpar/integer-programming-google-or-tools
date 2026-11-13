from scan import scan

HEADER = [
    "MIP schedule has 310 rows; 520 cols; 2104 nonzeros; 480 integer variables (480 binary)",
    "Coefficient ranges:",
    "  Matrix  [1e-02, 1e+09]",
    "  Cost    [1e+00, 3e+05]",
    "  Bound   [1e+00, 1e+00]",
    "  RHS     [1e+00, 4e+07]",
    "WARNING: Problem has some excessively large row bounds",
    "Presolving model",
]
REPORT = [
    "  Solution status   feasible",
    "                    81250 (objective)",
    "                    4.2e-07 (int. viol.)",
]
CLEAN = [
    "MIP schedule has 310 rows; 520 cols; 2104 nonzeros; 480 integer variables (480 binary)",
    "Coefficient ranges:",
    "  Matrix  [1e+00, 6e+03]",
    "  Cost    [1e+00, 3e+03]",
    "  Bound   [1e+00, 1e+00]",
    "  RHS     [1e+00, 4e+02]",
    "Presolving model",
    "  Solution status   feasible",
    "                    81.25 (objective)",
]


def test_a_troubled_log_gives_its_findings_in_order_and_a_clean_one_none():
    assert scan(HEADER + REPORT) == [
        "matrix span 1e+11",
        "warning: Problem has some excessively large row bounds",
        "integrality violation 4.2e-07",
    ]
    assert scan(CLEAN) == []


def test_a_zero_violation_is_not_a_finding():
    lines = ["                    0 (bound viol.)", "                    3e-08 (row viol.)"]
    assert scan(lines) == ["row violation 3e-08"]


def test_a_span_at_the_limit_is_not_a_finding():
    assert scan(["  Matrix  [1e+00, 1e+06]"]) == []
    assert scan(["  Matrix  [1e+00, 2e+06]"]) == ["matrix span 2e+06"]


def test_the_cost_range_is_not_the_matrix_span():
    lines = ["  Matrix  [1e+00, 1e+08]", "  Cost    [1e-03, 1e+09]", "  RHS     [1e-05, 1e+05]"]
    assert scan(lines) == ["matrix span 1e+08"]
