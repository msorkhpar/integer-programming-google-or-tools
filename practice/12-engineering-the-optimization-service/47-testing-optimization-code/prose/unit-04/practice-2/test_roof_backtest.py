from roof_backtest import summarize


def test_a_cycle_is_split_into_kept_added_and_dropped():
    archive = [{"cycle": 2024, "approved": {"gym": 2025, "lab": 2025, "hall": 2027}}]
    rerun = {2024: {"gym": 2025, "pool": 2026}}
    assert summarize(archive, rerun) == [
        {"cycle": 2024, "missing": False, "kept": 1, "moved": 0, "added": 1, "dropped": 2, "agreement": 0.333}]


def test_a_project_in_another_year_is_moved_not_kept():
    archive = [{"cycle": 2025, "approved": {"gym": 2026, "lab": 2026, "hall": 2027}}]
    rerun = {2025: {"gym": 2027, "lab": 2026, "hall": 2027}}
    assert summarize(archive, rerun) == [
        {"cycle": 2025, "missing": False, "kept": 2, "moved": 1, "added": 0, "dropped": 0, "agreement": 0.667}]


def test_a_cycle_with_no_rerun_is_marked_missing():
    archive = [{"cycle": 2024, "approved": {"gym": 2025}}, {"cycle": 2025, "approved": {"lab": 2026}}]
    rerun = {2025: {"lab": 2026}}
    assert summarize(archive, rerun) == [
        {"cycle": 2024, "missing": True},
        {"cycle": 2025, "missing": False, "kept": 1, "moved": 0, "added": 0, "dropped": 0, "agreement": 1.0}]


def test_an_empty_approved_plan_agrees_with_an_empty_rerun():
    archive = [{"cycle": 2026, "approved": {}}, {"cycle": 2027, "approved": {}}]
    rerun = {2026: {}, 2027: {"gym": 2028}}
    assert summarize(archive, rerun) == [
        {"cycle": 2026, "missing": False, "kept": 0, "moved": 0, "added": 0, "dropped": 0, "agreement": 1.0},
        {"cycle": 2027, "missing": False, "kept": 0, "moved": 0, "added": 1, "dropped": 0, "agreement": 0.0}]
