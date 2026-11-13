## ADDED Requirements

### Requirement: Scenario traceability
The checker SHALL trace each scenario of the living specs to its test, and SHALL report every
scenario with no test and every test of a capability's test file that traces to no scenario. A
scenario's test is named test_ and the scenario's name in lower case, each run of other characters
an underscore, in tests/test_ and the capability's name, with hyphens as underscores, and .py.

#### Scenario: A scenario with no test is reported
- **GIVEN** a spec with the scenarios Fits and Too big, and a test file with test_fits only
- **WHEN** the checker traces
- **THEN** it reports Too big as a scenario with no test

#### Scenario: A test with no scenario is reported
- **GIVEN** a spec with the scenario Fits, and a test file with test_fits and test_old_rule
- **WHEN** the checker traces
- **THEN** it reports test_old_rule as a test with no scenario

#### Scenario: A test in the file of another capability does not count
- **GIVEN** capabilities demo and other, and test_fits written in other's test file
- **WHEN** the checker traces
- **THEN** it reports demo's scenario Fits as untested, and other's test_fits as a test with no scenario

#### Scenario: These specs and tests trace both ways
- **WHEN** the checker traces this project's living specs and tests
- **THEN** it reports no scenario without a test and no test without a scenario
