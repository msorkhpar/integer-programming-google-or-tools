# 2.4. LP Solvers in Practice

The three ways an LP gets solved and what each returns: simplex (GLOP, HiGHS), interior point
(HiGHS's barrier) and the first-order method PDLP, all on one GridCap funding LP; how to check that
they agree; how to read a solver's log from header to verdict; and how to answer what-if questions
by editing the model and re-solving from the last answer, or from a dual value alone. GridCap, the
running dataset, is a fictional utility's portfolio, not real data.

## Contents

1. [Simplex, interior point and PDLP: GLOP, HiGHS, PDLP](README_2.4.1.md)
2. [Reading an LP solver log](README_2.4.2.md)
3. [Re-solving after the data changes](README_2.4.3.md)
