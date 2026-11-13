## Purpose
The format rules specs_check.py applies to this project's openspec/ folder: the rules of
`openspec validate --strict` that these specs need, mirrored in Python for the course's runner.

## ADDED Requirements

### Requirement: Requirement text
The checker SHALL report an error for a requirement with no text under its header.

#### Scenario: A requirement with no text is an error
- **WHEN** a requirement has a header and a scenario but no text
- **THEN** the checker reports one error, naming the requirement

### Requirement: Normative keyword
The checker SHALL report a warning for a requirement whose text has neither SHALL nor MUST.

#### Scenario: Text without SHALL or MUST is a warning
- **WHEN** a requirement's text reads "The planner keeps the budget."
- **THEN** the checker reports one warning, naming the requirement

#### Scenario: A keyword only in the header does not count
- **WHEN** the requirement's header has SHALL and the text under it has neither keyword
- **THEN** the checker reports the same warning

### Requirement: At least one scenario
The checker SHALL report an error for a requirement with no scenario that has steps under it.

#### Scenario: A requirement without scenarios is an error
- **WHEN** a requirement has text and no scenario
- **THEN** the checker reports one error, naming the requirement

#### Scenario: An empty scenario does not count
- **WHEN** a requirement's only scenario is a header with nothing under it
- **THEN** the checker reports the same error

### Requirement: Scenario steps
The checker SHALL report a warning for a scenario with no WHEN or GIVEN step, or with no THEN step.

#### Scenario: A scenario without THEN is a warning
- **WHEN** a scenario has a WHEN step and no THEN step
- **THEN** the checker reports one warning, naming the scenario

### Requirement: Strict validation
The checker SHALL fail a spec that has a warning in strict mode, as `openspec validate --strict`
does, and pass it in plain mode.

#### Scenario: Strict mode fails on a warning
- **WHEN** a spec's only issue is a warning
- **THEN** it passes in plain mode and fails in strict mode

#### Scenario: These specs pass strict validation
- **WHEN** the checker validates this project's openspec/ folder in strict mode
- **THEN** every living spec and every active change passes
