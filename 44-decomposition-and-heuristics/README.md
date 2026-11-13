# 11.3. Decomposition and Heuristics

When one model is too big or too slow, split it, and say honestly how good the answer is: a
Lagrangian bound from prices on the rows that tie the plan together, a Benders loop that keeps the
yes/no decisions apart from an LP per year, logic-based Benders with a CP-SAT scheduling check,
column generation of crew-day patterns, and the rolling-horizon and LNS heuristics, each checked
against the model solved whole or against the best bound known.

## Contents

1. [Lagrangian relaxation and subgradient optimization](README_11.3.1.md)
2. [Benders decomposition](README_11.3.2.md)
3. [Logic-based Benders](README_11.3.3.md)
4. [Column generation in one worked example](README_11.3.4.md)
5. [Rolling horizon and LNS heuristics](README_11.3.5.md)
