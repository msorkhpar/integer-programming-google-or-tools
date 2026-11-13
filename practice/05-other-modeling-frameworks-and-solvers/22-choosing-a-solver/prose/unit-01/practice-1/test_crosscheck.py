from crosscheck import suspects

AGREE = {"Kestrel": ("OPTIMAL", 812.5), "Osprey": ("OPTIMAL", 812.5), "Merlin": ("OPTIMAL", 812.5)}


def test_a_solver_off_the_others_is_a_suspect():
    assert suspects({**AGREE, "Harrier": ("OPTIMAL", 790.0)}, 0.01) == ["Harrier"]


def test_a_deviation_above_counts_too():
    assert suspects({**AGREE, "Harrier": ("OPTIMAL", 790.0)}, 1e-6) == ["Harrier"]
    assert suspects({**AGREE, "Harrier": ("OPTIMAL", 830.0)}, 1e-6) == ["Harrier"]


def test_the_reference_is_the_median_not_the_mean():
    results = {**AGREE, "Harrier": ("OPTIMAL", 8125.0)}             # a mean of 2,640.6 would flag all four
    assert suspects(results, 1e-6) == ["Harrier"]


def test_runs_that_did_not_prove_optimality_are_left_out():
    results = {"Kestrel": ("OPTIMAL", 812.5), "Osprey": ("TIME_LIMIT", 700.0), "Merlin": ("OPTIMAL", 790.0),
               "Harrier": ("OPTIMAL", 812.5)}
    assert suspects(results, 1e-6) == ["Merlin"]                     # with 700 in, the median would be 801.25


def test_a_difference_within_the_tolerance_is_allowed():
    results = {**AGREE, "Harrier": ("OPTIMAL", 812.5 + 0.0008)}      # 0.0008 <= 1e-6 * 812.5
    assert suspects(results, 1e-6) == []
    assert suspects({**AGREE, "Harrier": ("OPTIMAL", 812.5 + 0.0009)}, 1e-6) == ["Harrier"]
