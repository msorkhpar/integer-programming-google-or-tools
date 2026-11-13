# Proposal: Carry unspent budget into the next year

## Why
Finance now lets money a year leaves unspent move into the next year, up to a fifth of one year's
budget. The planner still treats each year's budget as use-it-or-lose-it, so a large project that
needs a little more than one year's money can never start, even after a light year.

## What Changes
- Unspent money of a plan year carries into the next year, up to the request's carry-over percent
  of one yearly budget. No year may spend money from a later year.
- The yearly budget requirement changes, and its name says so.
- A carry-over percent outside 0 to 100 is refused before solving.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `capital-plan`: the yearly budget requirement is renamed and modified, and a check is added.

## Impact
- Code: Request.carry, request.check, the carry variables and budget rows in model.build,
  report.carry_by_year.
- Tests: four new tests; the two budget tests stay as they are, since a request with no carry-over
  keeps the old rule.
