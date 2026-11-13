## ADDED Requirements

### Requirement: Must-do override
The planner SHALL start every project the request marks must-do, in a year of its window, whatever
the project is worth.

#### Scenario: A must-do project is started
- **GIVEN** a project worth less per $k than every other
- **WHEN** the request marks it must-do, with a reason
- **THEN** the plan starts it

#### Scenario: A plan without the must-do is refused
- **GIVEN** a request that marks project L must-do
- **WHEN** a plan leaves L out
- **THEN** the plan is refused
- **AND** the plan that starts L is allowed

### Requirement: Recorded reason
The planner SHALL refuse, before solving, a must-do override whose reason is empty or only spaces.

#### Scenario: An override with an empty reason is refused
- **WHEN** a request marks a project must-do with an empty reason
- **THEN** the planner refuses it with a message
- **AND** the same override with a reason is accepted

#### Scenario: A reason of only spaces is refused
- **WHEN** a request marks a project must-do with a reason of three spaces
- **THEN** the planner refuses it with a message

### Requirement: Override target
The planner SHALL refuse, before solving, a must-do override for a project that is not in the
portfolio or that cannot start in any plan year.

#### Scenario: An override for an unknown project is refused
- **WHEN** a request marks project Z must-do and the portfolio has no Z
- **THEN** the planner refuses it with a message

#### Scenario: A must-do that cannot start in the plan is refused
- **GIVEN** a project that may start only in 2030, in a plan of 2027 to 2029
- **WHEN** a request marks it must-do
- **THEN** the planner refuses it with a message naming the project

### Requirement: Overrides are reported
The planner SHALL list each must-do override with its recorded reason in the plan's report.

#### Scenario: The report lists each override with its reason
- **WHEN** a request marks two projects must-do
- **THEN** the report lists both, by project id, each with its reason
