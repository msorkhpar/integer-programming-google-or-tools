"""Lesson 14.4.1: the planner as it is, its tests as scenarios, and the baseline change replayed.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/00, then steps/01.
"""

import re
import tempfile
from collections import Counter
from pathlib import Path

import changes
import steps

steps.use(0)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import generate     # noqa: E402
from capplan.request import Request        # noqa: E402

PORTFOLIO = generate(40, seed=58, years=5)
REQUEST = Request(budget=3_000, years=5)


def test_name(scenario: str) -> str:
    return "test_" + re.sub(r"[^a-z0-9]+", "_", scenario.lower()).strip("_")


got = plan(PORTFOLIO, REQUEST)
per_year = Counter(got.starts.values())
print(f"40 fictional projects, $3,000k a year for 2027-2031: {len(got.starts)} started, "
      f"value ${got.value:,}k ({got.status})")
print("starts per year: " + ", ".join(f"{y} {per_year[y]}" for y in REQUEST.plan_years()))

checker = changes.checker_module(1)
delta = (changes.change_of(1) / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
old_tests = {name.split("::")[1] for name in steps.test_sources(0)}
print("capital-plan scenarios, and the test of steps/00 each one names:")
for req in checker.read_delta(delta).added:
    for scenario in req.scenarios:
        print(f"  {scenario:48} {test_name(scenario)} ({'in' if test_name(scenario) in old_tests else 'NOT in'} steps/00)")

print("\n== validate --strict, the change proposed, with the checker of steps/00 (a stub)")
changes.validate(1, 0)
print("\n== validate --strict, the change proposed, with the checker of steps/01")
changes.validate(1, 1)

print("\n== the capital-plan delta with two faults planted, then a third")
for label, text in changes.planted(delta):
    issues, count = checker.check_delta(text, None, "add-baseline-specs/specs/capital-plan/spec.md")
    print(f"-- {label}")
    for issue in issues:
        print(issue)
    print(f"plain validation {'passes' if checker.passes(issues, strict=False) else 'fails'}; "
          f"strict validation {'passes' if checker.passes(issues) else 'fails'}")

print("\n== archive")
changes.archive(1)
print()
steps.show(1)
