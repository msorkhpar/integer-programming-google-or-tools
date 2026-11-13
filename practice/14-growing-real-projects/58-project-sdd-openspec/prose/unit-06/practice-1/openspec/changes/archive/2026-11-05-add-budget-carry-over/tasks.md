# Tasks

## 1. Tests from the scenarios
- [x] 1.1 Add Request.carry as a stub that the model ignores
- [x] 1.2 Write one test per new scenario; keep the two budget tests unchanged
- [x] 1.3 Run them on the code before the change and see each new test fail on an assertion

## 2. Code
- [x] 2.1 model.build: carry_<year>, between 0 and the cap, for every plan year but the last
- [x] 2.2 model.build: budget_<year> as a balance with the carry in and the carry out
- [x] 2.3 request.check: refuse a carry-over outside 0 to 100
- [x] 2.4 report.carry_by_year, counted from the starts
- [x] 2.5 Run every test, and `specs_check.py validate --strict`

## 3. Archive
- [x] 3.1 Archive the change
