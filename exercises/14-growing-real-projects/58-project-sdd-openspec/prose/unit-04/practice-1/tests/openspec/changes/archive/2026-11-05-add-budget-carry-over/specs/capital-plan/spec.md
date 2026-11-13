## RENAMED Requirements
- FROM: `### Requirement: Yearly budget`
- TO: `### Requirement: Yearly budget with carry-over`

## MODIFIED Requirements

### Requirement: Yearly budget with carry-over
The planner SHALL keep what the plan spends in each plan year within the yearly budget plus the
money carried into that year, counting each project's whole cost in the year it starts. Money a
year leaves unspent SHALL carry into the next year, up to the request's carry-over percent of one
yearly budget, and no year SHALL spend money of a later year.

#### Scenario: Spending up to the budget is allowed
- **GIVEN** a budget of $1,000k a year and no carry-over
- **WHEN** a plan starts a $600k project and a $400k project in 2027
- **THEN** the plan is allowed

#### Scenario: Spending over the budget is refused
- **GIVEN** a budget of $1,000k a year and no carry-over
- **WHEN** a plan starts a $600k project and a $410k project in 2027
- **THEN** the plan is refused

#### Scenario: Unspent money carries into the next year
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $800k in 2027 and $1,200k in 2028
- **THEN** the plan is allowed
- **AND** the same plan with $10k more in 2028 is refused

#### Scenario: Carry-over above its cap is refused
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $500k in 2027 and $1,250k in 2028
- **THEN** the plan is refused, since only $200k of the $500k left may carry
- **AND** the plan that spends $1,200k in 2028 is allowed

#### Scenario: Money cannot be borrowed from a later year
- **GIVEN** a budget of $1,000k a year and a carry-over of 20%
- **WHEN** a plan spends $1,100k in 2027 and $900k in 2028
- **THEN** the plan is refused
- **AND** the plan that spends $900k in 2027 and $1,100k in 2028 is allowed

## ADDED Requirements

### Requirement: Carry-over is checked before solving
The planner SHALL refuse, before solving, a carry-over percent outside 0 to 100.

#### Scenario: A carry-over outside 0 to 100 percent is refused
- **WHEN** a request sets a carry-over of 101% or of -1%
- **THEN** the planner refuses it with a message
- **AND** a carry-over of 100% is accepted
