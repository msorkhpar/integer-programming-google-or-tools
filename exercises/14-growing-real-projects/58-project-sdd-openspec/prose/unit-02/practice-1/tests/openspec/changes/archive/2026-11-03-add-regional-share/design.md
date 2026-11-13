# Design: A regional spend share

## Context
The model has a 0-1 start variable per project and plan year, and the yearly spend is a sum of
those variables times each project's cost. The planners answered two questions before this design:
the share is of what the plan spends, not of the budget, and it holds in every year, not over the
plan as a whole.

## Goals / Non-Goals

**Goals:**
- One row family that states the share with integer coefficients.

**Non-Goals:**
- A share of the budget, or a share over the whole plan.

## Decisions

### Decision: the share as a linear row
A share is a ratio of two spends, which is not linear. Multiplying both sides by the year's spend,
which is never negative, and by 100 gives one linear row per named region and year:
100 times the region's spend is at least the share times the year's spend. Every coefficient is an
integer, so a plan exactly at the share is allowed and one $k under it is refused. No new variable.

### Decision: a year with no spend needs no case of its own
The ratio is undefined when a year spends nothing, but the multiplied row reads 0 >= 0 and holds.

### Decision: refuse impossible shares before building the model
Shares that add up to more than 100 leave only years with no spend, and a share for a region with no
project leaves the same. The model would return an empty plan with no word about why, so request.check
refuses them first, with a message.

## Risks / Trade-offs
- A share makes the plan's value lower or equal; the lesson reports by how much on GridCap's
  40-project portfolio.
