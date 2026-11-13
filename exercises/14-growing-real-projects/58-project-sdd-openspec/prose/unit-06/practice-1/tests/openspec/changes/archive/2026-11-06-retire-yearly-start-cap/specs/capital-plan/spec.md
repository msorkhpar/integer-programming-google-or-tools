## REMOVED Requirements

### Requirement: Yearly start cap
**Reason**: The cap stood for the design-review board's capacity, which no longer limits starts.

**Migration**: Remove max_starts from requests. A request that still sets it is refused with a
message naming this change.

## ADDED Requirements

### Requirement: Retired start cap is refused
The planner SHALL refuse, before solving, a request that sets the retired yearly start cap, with a
message naming the change that retired it.

#### Scenario: A request that sets the retired cap is refused
- **WHEN** a request sets a start cap of 3
- **THEN** the planner refuses it with a message naming retire-yearly-start-cap
- **AND** a request that sets no cap is accepted

#### Scenario: A retired cap of zero is refused too
- **WHEN** a request sets a start cap of 0
- **THEN** the planner refuses it with the same message

### Requirement: Starts per year are not capped
The planner SHALL allow any number of projects to start in a plan year in which every other
requirement holds.

#### Scenario: Four starts in one year are allowed
- **GIVEN** a request that sets no start cap, and four $10k projects
- **WHEN** a plan starts all four in 2027
- **THEN** the plan is allowed
