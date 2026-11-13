import pytest

from imaging import Replacement, plan_score, project_score

REFERENCE = {"downtime_hours": 100, "scans_per_day": 10, "energy_mwh": 100}
WEIGHTS = {"downtime_hours": 0.5, "scans_per_day": 0.3, "energy_mwh": 0.2}


def machine(name, down, scans, energy):
    """Before and after levels: (before, after) pairs."""
    return Replacement(name, {"downtime_hours": down[0], "scans_per_day": scans[0], "energy_mwh": energy[0]},
                       {"downtime_hours": down[1], "scans_per_day": scans[1], "energy_mwh": energy[1]})


ALL = {p.name: p for p in [
    machine("MRI", (120, 20), (20, 26), (300, 250)),       # 0.5 x 1.0 + 0.3 x 0.6 + 0.2 x 0.5 = 0.78
    machine("CT", (80, 60), (30, 32), (200, 190)),         # 0.10 + 0.06 + 0.02 = 0.18
    machine("X-ray", (50, 40), (40, 41), (80, 70)),        # 0.05 + 0.03 + 0.02 = 0.10
    machine("Ultrasound", (40, 40), (25, 25), (60, 60)),   # no change at all
    machine("PET", (90, 50), (12, 14), (150, 200)),        # 0.20 + 0.06 - 0.10 = 0.16
]}


def score(plan):
    return plan_score(plan, ALL, REFERENCE, WEIGHTS)


def test_a_project_scores_its_weighted_improvements():
    assert project_score(ALL["MRI"], REFERENCE, WEIGHTS) == pytest.approx(0.78)
    assert project_score(ALL["CT"], REFERENCE, WEIGHTS) == pytest.approx(0.18)       # all three fall or rise the right way


def test_a_project_that_changes_nothing_adds_nothing():
    assert score(["CT", "X-ray"]) == pytest.approx(0.28)
    assert score(["CT", "X-ray", "Ultrasound"]) == pytest.approx(0.28)


def test_a_measure_that_gets_worse_counts_against_the_project():
    assert score(["PET"]) == pytest.approx(0.16)


def test_a_plan_is_worth_the_sum_of_its_projects():
    assert score(["MRI", "CT", "X-ray"]) == pytest.approx(1.06)
    assert score([]) == 0
