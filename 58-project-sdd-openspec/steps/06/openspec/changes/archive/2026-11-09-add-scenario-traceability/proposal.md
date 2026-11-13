# Proposal: Trace every scenario to a test

## Why
GridCap's auditors ask two questions of every rule the planner keeps: which test shows it holds, and
which agreed rule each test checks. Today nothing answers either. The must-do change was archived
with two tasks open, a scenario with no test and no code, and no check noticed.

## What Changes
- specs_check.py traces each scenario of the living specs to the test named after it, and reports
  every scenario with no test and every test that names no scenario.
- The open tasks of add-must-do-override are done: the test of "A must-do that cannot start in the
  plan is refused", and the check it needs. The capital-plan spec already states the scenario, so
  it does not change.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `spec-checks`: a traceability requirement is added.

## Impact
- Code: trace and test_name in specs_check.py; the window check in request.check.
- Tests: four tests in tests/test_spec_checks.py, one in tests/test_capital_plan.py.
