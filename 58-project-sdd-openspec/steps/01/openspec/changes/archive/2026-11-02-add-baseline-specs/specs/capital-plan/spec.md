## Purpose
Which of GridCap's capital projects the planner starts, and in which year, within the planners'
budget and rules. GridCap is a fictional utility.

## ADDED Requirements

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
