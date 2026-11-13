import tomllib
from pathlib import Path

import renewal
from renewal.cli import main
from renewal.finance import finance_lines
from renewal.fleet import generate_fleet
from renewal.plan import plan
from renewal.report import spend_by_year
from renewal.request import Request

HERE = Path(__file__).parent
SMALL = ["--units", "30", "--budget", "1200", "--gap", "0"]


def test_the_finance_lines_add_up_to_the_plan():
    fleet = generate_fleet(40)
    request = Request(budget=1500, years=4, window=10, min_age=40, outage_cost=300, crew_weeks=12)
    got = plan(fleet, request)
    lines = finance_lines(fleet, request, got)
    assert [ln.year for ln in lines] == [2027, 2028, 2029, 2030]
    assert sum(ln.units for ln in lines) == len(got.replace) > 0
    assert {ln.year: ln.total for ln in lines if ln.total} == spend_by_year(fleet, got.replace, 300)
    assert all(ln.total == ln.replacement + ln.outage_cost <= ln.budget for ln in lines)
    assert abs(sum(ln.risk_removed for ln in lines) - got.value) < 1e-6


def test_the_report_matches_the_reviewed_golden_file(tmp_path):
    assert main(SMALL + ["--out", str(tmp_path / "plan.md")]) == 0
    assert (tmp_path / "plan.md").read_text() == (HERE / "golden" / "plan_30.md").read_text()


def test_two_runs_write_the_same_report(tmp_path):
    assert main(SMALL + ["--out", str(tmp_path / "a.md")]) == 0
    assert main(SMALL + ["--out", str(tmp_path / "b.md")]) == 0
    assert (tmp_path / "a.md").read_text() == (tmp_path / "b.md").read_text()


def test_the_package_declares_its_version_and_command():
    project = tomllib.loads((HERE.parent / "pyproject.toml").read_text()).get("project", {})
    assert project.get("scripts", {}).get("renewal") == "renewal.cli:main"
    assert project.get("version") == getattr(renewal, "__version__", None)
