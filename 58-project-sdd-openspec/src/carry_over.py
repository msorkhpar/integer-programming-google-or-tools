"""Lesson 14.4.4: carry-over, a MODIFIED budget rule and a RENAMED requirement.

The portfolio is generated (GridCap is fictional). The code is snapshot steps/03, then steps/04.
"""

import changes
import steps

BUDGET, YEARS, SHARES = 3_000, 5, {"plains": 25}
MUST_DO = {"P039": "Regulator order RO-7, Plainsview feeder"}


def by_year(values: dict) -> str:
    return " ".join(f"{values.get(y, 0):5,}" for y in range(2027, 2027 + YEARS))


steps.use(3)
from capplan.plan import plan              # noqa: E402
from capplan.portfolio import generate     # noqa: E402
from capplan.request import Request        # noqa: E402

PORTFOLIO = generate(40, seed=58, years=YEARS)
before = plan(PORTFOLIO, Request(budget=BUDGET, years=YEARS, shares=SHARES, must_do=MUST_DO))

steps.use(4)
from capplan.plan import plan              # noqa: E402
from capplan.report import carry_by_year, spend_by_year   # noqa: E402
from capplan.request import Request        # noqa: E402

print(f"{'':36} {'value':>8}  spend by year, 2027 to 2031    carried out of each year")
print(f"{'steps/03, start cap 3':36} ${before.value:>7,}k  {by_year(spend_by_year(PORTFOLIO, before.starts))}")
for cap in (3, None):
    for carry in (0, 20):
        request = Request(budget=BUDGET, years=YEARS, shares=SHARES, must_do=MUST_DO, carry=carry, max_starts=cap)
        got = plan(PORTFOLIO, request)
        label = f"steps/04, start cap {cap or 'none'}, carry {carry}%"
        print(f"{label:36} ${got.value:>7,}k  {by_year(spend_by_year(PORTFOLIO, got.starts))}"
              f"    {by_year(carry_by_year(PORTFOLIO, got.starts, request))}")

checker = changes.checker_module(4)
living = (steps.step_dir(3) / "openspec" / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
delta = (changes.change_of(4) / "specs" / "capital-plan" / "spec.md").read_text(encoding="utf-8")
print("\n== the delta as written")
print(f"issues: {len(checker.check_delta(delta, living, 'capital-plan')[0])}")
dropped = delta.replace("""#### Scenario: Spending over the budget is refused
- **GIVEN** a budget of $1,000k a year and no carry-over
- **WHEN** a plan starts a $600k project and a $410k project in 2027
- **THEN** the plan is refused

""", "")
old_name = delta.replace("## MODIFIED Requirements\n\n### Requirement: Yearly budget with carry-over",
                         "## MODIFIED Requirements\n\n### Requirement: Yearly budget")
for label, text in (("== a MODIFIED block that drops a scenario", dropped),
                    ("== a MODIFIED block under the old name", old_name)):
    print(label)
    for issue in checker.check_delta(text, living, "capital-plan")[0]:
        print(issue)

print("\n== validate --strict, the change proposed")
changes.validate(4, 4)
print()
steps.show(4)
print("\n== archive")
changes.archive(4)
