# Tasks

## 1. Tests from the scenarios
- [x] 1.1 Add Request.must_do and report.overrides as stubs
- [x] 1.2 Test: a must-do project is started
- [x] 1.3 Test: a plan without the must-do is refused
- [x] 1.4 Test: an override with an empty reason, or a reason of only spaces, is refused
- [x] 1.5 Test: an override for an unknown project is refused
- [ ] 1.6 Test: a must-do that cannot start in the plan is refused
- [x] 1.7 Test: the report lists each override with its reason
- [x] 1.8 Run the tests on the code before the change and see each fail on an assertion

## 2. Code
- [x] 2.1 model.build: the row must_<pid>, the project's starts summing to exactly 1, in place of once_<pid>
- [x] 2.2 request.check: refuse an unknown project, and a reason that is empty or only spaces
- [ ] 2.3 request.check: refuse a must-do whose window has no plan year
- [x] 2.4 report.overrides
- [x] 2.5 Run every test, and `specs_check.py validate --strict`

## 3. Archive
- [x] 3.1 Archive the change
