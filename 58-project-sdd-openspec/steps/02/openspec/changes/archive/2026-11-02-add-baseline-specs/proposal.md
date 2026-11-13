# Proposal: Baseline specs for the capital planner

## Why
The planner's rules live only in its code and in six tests. Before the planners change a rule (a
regional share is next), the team needs today's rules written as requirements a planner can read
and a test can check, and a checker that keeps those specs in OpenSpec's format.

## What Changes
- Specify the planner as it is today: the yearly budget, one start per project, start windows, the
  yearly start cap and the most valuable plan. The planner's behaviour does not change.
- Specify the rules the checker applies to requirements and scenarios, and write them in
  specs_check.py.

## Capabilities

### New Capabilities
- `capital-plan`: which projects the planner starts, and in which year.
- `spec-checks`: the format rules specs_check.py applies to this project's specs.

### Modified Capabilities
None.

## Impact
- Specs: openspec/specs/capital-plan/spec.md and openspec/specs/spec-checks/spec.md, both new.
- Code: check_requirement in specs_check.py. The planner's code does not change.
- Tests: tests/test_spec_checks.py, new; the six planner tests stay, each named after its scenario.
