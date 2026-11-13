# 8.2. Lexicographic Objectives

Ranking objectives instead of weighting them: the first objective is optimized, a tolerance turns it
into a floor, and the next objective chooses among the plans above that floor. Measured on GridCap
small with NPV and risk removed, as a relative share and as an absolute amount, and then built three
ways (MathOpt's prioritized objectives, gurobipy's `setObjectiveN` and a manual two-pass solve) that
return the same plan.

## Contents

1. [Hierarchical objectives with tolerances](README_8.2.1.md)
2. [Three implementations: auxiliary objectives in MathOpt, `setObjectiveN` in gurobipy, and a manual two-pass solve](README_8.2.2.md)
