# Proposal: Retire the yearly start cap

## Why
The cap of three starts a year stood for the capacity of the design-review board, which met once a
quarter. Reviews are now done as each design is ready, so the cap no longer stands for anything,
and it keeps the planner from starting four small projects in a year that has the money for them.

## What Changes
- **BREAKING**: the yearly start cap is removed from the planner, along with its default of 3.
- A request that still sets the cap is refused before solving, with a message that names this
  change, so that no caller gets a different plan without being told.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `capital-plan`: the yearly start cap is removed; two requirements are added for what replaces it.

## Impact
- Code: the starts rows leave model.build; request.check refuses max_starts; its default becomes None.
- Tests: the cap's test is deleted with its scenario; three tests are added.
- Callers: any request that sets max_starts must drop it.
