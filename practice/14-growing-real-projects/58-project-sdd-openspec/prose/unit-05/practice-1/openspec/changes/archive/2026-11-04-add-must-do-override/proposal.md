# Proposal: A must-do override with a recorded reason

## Why
Some projects must be done whatever the model thinks they are worth: a regulator's order, storm
damage, a safety finding. Planners now force them by editing the portfolio's values by hand, which
leaves no record of who forced what, or why, and changes the plan's reported value.

## What Changes
- A request may mark projects must-do, each with the reason it is forced; the plan starts every
  must-do project in a year of its window.
- An override with no reason, or for a project the planner cannot start, is refused before solving.
- The report lists each override with its reason.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `capital-plan`: four requirements are added, for the override, its reason, its target and its report.

## Impact
- Code: Request.must_do, request.check, the must rows in model.build, report.overrides.
- Tests: one test per scenario in tests/test_capital_plan.py.
