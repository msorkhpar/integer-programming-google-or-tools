# 11.2. Warm Starts and Tuning

Making a solver reach a good plan sooner without changing the model: starting each planning cycle
from last cycle's approved plan, choosing the few parameters that matter (presolve, cuts,
heuristics and the solver's focus), and tuning them automatically without fooling yourself. Every
claim is measured the way lesson 5.4.2 taught: deterministic work units, several seeds, a fixed
instance set, and ratios of shifted geometric means. GridCap is a fictional utility.

## Contents

1. [MIP starts from last cycle's plan](README_11.2.1.md)
2. [The parameters that matter: presolve, cuts, heuristics, focus](README_11.2.2.md)
3. [Automated tuning, and how not to overfit it](README_11.2.3.md)
