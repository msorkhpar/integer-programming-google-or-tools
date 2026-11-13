# capital-plan Specification

## Purpose
Which of GridCap's capital projects the planner starts, and in which year, within the planners'
budget and rules. GridCap is a fictional utility.

## Requirements

### Requirement: Yearly budget
The planner SHALL keep what the plan spends in each plan year within the yearly budget, counting
each project's whole cost in the year it starts.

#### Scenario: Spending up to the budget is allowed
- **GIVEN** a budget of $1,000k a year
- **WHEN** a plan starts a $600k project and a $400k project in 2027
- **THEN** the plan is allowed

#### Scenario: Spending over the budget is refused
- **GIVEN** a budget of $1,000k a year
- **WHEN** a plan starts a $600k project and a $410k project in 2027
- **THEN** the plan is refused

### Requirement: One start per project
The planner SHALL start each project at most once in the plan.

#### Scenario: A project started twice is refused
- **WHEN** a plan starts project A in 2027 and again in 2028
- **THEN** the plan is refused
- **AND** the plan that starts A in 2027 only is allowed

### Requirement: Start window
The planner SHALL start a project only in a plan year from its earliest to its latest start year.

#### Scenario: A start outside the window is refused
- **GIVEN** a project that may start in 2028 only, in a plan of 2027 to 2029
- **WHEN** a plan starts it in 2027, or in 2030
- **THEN** the plan is refused
- **AND** the plan that starts it in 2028 is allowed

### Requirement: Yearly start cap
The planner SHALL start no more projects in a year than the request's start cap, which is 3 when
the request does not set one.

#### Scenario: More starts than the cap are refused
- **GIVEN** a request that does not set a start cap
- **WHEN** a plan starts four projects in 2027
- **THEN** the plan is refused
- **AND** a plan that starts three of them in 2027 is allowed

### Requirement: Most valuable plan
The planner SHALL return a plan of the greatest total value among the plans that keep every
requirement.

#### Scenario: The plan has the greatest value within the rules
- **GIVEN** five projects and a two-year plan
- **WHEN** the planner plans
- **THEN** the plan's value equals the best value found by trying every plan

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
