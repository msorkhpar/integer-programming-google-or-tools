## ADDED Requirements

### Requirement: Regional spend share
The planner SHALL give each region the request names at least its share, in whole percent, of what
the plan spends in every plan year.

#### Scenario: A share is kept at its boundary
- **GIVEN** a share of 25% for Plains
- **WHEN** a plan spends $1,000k in 2027, $250k of it on Plains
- **THEN** the plan is allowed
- **AND** the same plan with a $10k North project added in 2027 is refused

#### Scenario: A year with no spend keeps the share
- **GIVEN** a share of 25% for Plains
- **WHEN** a plan spends nothing in 2028
- **THEN** 2028 keeps the share
- **AND** a plan whose only 2028 start is a North project is refused

#### Scenario: The plan keeps every share
- **GIVEN** three projects whose most valuable plan, with no share, starts no Plains project
- **WHEN** the planner plans with a share of 25% for Plains
- **THEN** every year of the plan gives Plains at least 25% of its spend

### Requirement: Shares are checked before solving
The planner SHALL refuse, before solving, a request whose shares no plan with any spend could keep.

#### Scenario: A share outside 0 to 100 is refused
- **WHEN** a request sets a share of 101% or of -5%
- **THEN** the planner refuses it with a message
- **AND** a share of 100% is accepted

#### Scenario: Shares adding up to more than 100 are refused
- **WHEN** a request sets 60% for Plains and 50% for Coast
- **THEN** the planner refuses it with a message
- **AND** 40% for Plains and 60% for Coast is accepted

#### Scenario: A share for a region with no project is refused
- **GIVEN** a portfolio with Plains and North projects only
- **WHEN** a request sets a share for Coast
- **THEN** the planner refuses it with a message
