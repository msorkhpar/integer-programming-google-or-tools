A water utility (a fictional one) keeps its stakeholder-requirements worksheet as data. Each
requirement is a dictionary `{"id", "stakeholder", "text"}`. Each automated check that ran on the
latest plan is a dictionary `{"name", "covers", "passed"}`, where `covers` lists the requirement
ids the check proves. Before the plan goes to the regulator, the team wants the worksheet's
status, requirement by requirement and stakeholder by stakeholder.

Write two functions in `worksheet.py`:

- `trace(requirements, checks)`: each requirement id mapped to one of three states. **UNTESTED**
  when no check covers it; **MET** when at least one check covers it and every check covering it
  passed; **FAILED** when a check covering it failed.
- `by_stakeholder(requirements, status)`: for each stakeholder, how many of their requirements are
  in each of the three states, with every state present, zero or not.

Before you code, take a requirement covered by two checks, one passed and one failed, and say which
state it is in and why the worksheet must not call it met. The tests use small hand-made
worksheets. About twenty lines.
