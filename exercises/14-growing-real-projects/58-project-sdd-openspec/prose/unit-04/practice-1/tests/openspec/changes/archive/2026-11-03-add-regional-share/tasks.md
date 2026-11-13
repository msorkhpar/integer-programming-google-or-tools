# Tasks

## 1. Tests from the scenarios
- [x] 1.1 Add Request.shares as a stub that the model ignores
- [x] 1.2 Write one test per scenario in tests/test_capital_plan.py
- [x] 1.3 Run them on the code before the change and see each fail on an assertion

## 2. Code
- [x] 2.1 request.check: refuse shares outside 0 to 100, over 100 in total, or for a region with no project
- [x] 2.2 model.build: one row share_<region>_<year> for each named region with a share above 0, and each year
- [x] 2.3 report.share_by_year, counted from the starts, apart from the model
- [x] 2.4 Run every test, and `specs_check.py validate --strict`

## 3. Archive
- [x] 3.1 Archive the change
