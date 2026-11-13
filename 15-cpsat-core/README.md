# 4.4. CP-SAT Core

OR-Tools' constraint solver, CP-SAT, from the ground up: a model of bounded integer and Boolean
variables with whole-number linear rows; its own logic constraints (`add_bool_or`,
`add_implication`, `only_enforce_if`), which state GridCap's bundle rules with no big-M; objectives,
how fractional data is scaled to whole numbers, and solution callbacks that watch the search and
list every optimal plan; and, measured on GridCap-style models, the kinds of model where CP-SAT
beats a MIP solver and the kinds where it does not.

## Contents

1. [Integer and Boolean variables, linear constraints over integers](README_4.4.1.md)
2. [Native logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf`](README_4.4.2.md)
3. [Objectives, integer scaling and solution callbacks](README_4.4.3.md)
4. [When CP-SAT beats MIP, and when it doesn't](README_4.4.4.md)
