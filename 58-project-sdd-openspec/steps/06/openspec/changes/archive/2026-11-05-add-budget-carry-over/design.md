# Design: Carry unspent budget into the next year

## Context
Each plan year has a budget row: the year's spend is at most the yearly budget. Carry-over links
consecutive years, so the rows can no longer be written one year at a time from the starts alone.

## Goals / Non-Goals

**Goals:**
- Money moves forward only, never back, and never more than the cap.
- A request with a carry-over of 0 gives the same model as before.

**Non-Goals:**
- Carrying money past the plan's last year, or borrowing against a later year.

## Decisions

### Decision: one bounded integer variable per year that passes money on
carry_y, in $k, is what year y passes to year y + 1, for every plan year but the last. Its bounds
state two rules at once: the lower bound 0 forbids borrowing from a later year, and the upper bound,
the carry-over percent of one yearly budget rounded down, is the cap.

### Decision: the budget row becomes a balance
spend_y + carry_y <= budget + carry_(y-1), with carry of the year before the plan and carry of the
last year both 0. A year may pass on only what it was given and did not spend.

### Alternatives considered
- One pooled budget for the whole plan: simpler, but it lets one year spend the money of all the
  others, which finance did not allow.

## Risks / Trade-offs
- The carry variables are free in a plan that leaves money unused, so the solver's values say what is
  allowed, not what happened. The report counts what each year passes on from the starts alone.
