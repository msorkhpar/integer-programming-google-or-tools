# 6.2. Big-M and Indicators

Rules with an "unless" or an "or" in them: a limit a binary can switch off, written as a big-M row
with the smallest $`M`$ the data allow; what a loose $`M`$ does to the LP bound, to the search and to
the plans a solver calls optimal; the same rule as a MathOpt indicator constraint and as a CP-SAT
`only_enforce_if`; and disjunctions, written as big-M rows or as the tighter hull formulation.

## Contents

1. [Deriving big-M from bounds](README_6.2.1.md)
2. [What a loose M does to the LP bound and to numerics](README_6.2.2.md)
3. [Indicator constraints vs. big-M](README_6.2.3.md)
4. [Disjunctions: big-M vs. hull](README_6.2.4.md)
