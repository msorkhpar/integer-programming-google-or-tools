# Proposal: A regional spend share

## Why
The rate-case settlement for the Plains region commits GridCap to spend at least a quarter of each
year's capital spend on Plains projects. Plains projects are worth less per $k than the others, so
the planner, which keeps no such rule, leaves Plains short in most years.

## What Changes
- A request may name regions with a least share, in whole percent, of what the plan spends in every
  plan year, and the planner keeps every share in every year.
- Shares no plan could keep are refused before the planner solves.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `capital-plan`: two requirements are added, the regional share and the checks of shares.

## Impact
- Code: Request.shares, request.check, a share row family in model.build, report.share_by_year.
- Tests: six new tests in tests/test_capital_plan.py, one per scenario.
