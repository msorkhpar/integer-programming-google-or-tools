The planners checked the step-02 plan against their own lists and wrote back:

> Three must-do projects are missing: P010, P017 and P039 are regulatory commitments, so they go in
> whatever they're worth. P030 and P031 are two ways to fix the same Valley line, and you funded
> both. Also, P023 can only start a year after P022 has started, P016 needs P015, and P011 and P012
> are one Coast crew visit: both or neither. The export has all of this in its columns.

You start from the yearly planner of the lesson before. Make it keep the rules the export already
holds: a must-do project is funded, at most one project of an alternative group is funded, a bundle
is funded whole or not at all, and a child starts no earlier than its parent's start plus the lag.
Give each rule its own function in a new file, `cipt/rules.py`, that adds its rows under names the
planners can read, and let the model run the rules in turn. An export in which a project names a
parent the export does not have is refused when it is read.

`cipt/rules.py` starts as the reference has it, with the five rule functions of the blueprint
stubbed. Its imports are there (`Built` is imported inside `if TYPE_CHECKING:`, because `model.py`
imports `RULES` from `rules.py` and a plain import back would be circular), and so is `RULES`, the
tuple of rule functions `build` runs in order. `cipt/value.py` is the next lesson's stub, as the
reference has it; no code of this step imports it, so leave it as it is.

The expected report is one of several tied best plans. To print that one, create the start
variables project by project in export order, each project's start years in ascending order, and
run the rules in the order `once_or_must`, `alternatives`, `bundles`, `parents`, `budgets`. The
report's format is the one of the lesson before, unchanged.

Run executes `main.py`, which plans the demo export and prints the report; `expected/report.txt` is
the report it should print. Submit runs every test in `tests/`, the earlier steps' included, and
compares Run's report with the expected one.
