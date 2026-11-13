# 10.1. Numerics

Why a solver's "feasible" and "optimal" hold only to a tolerance, and what that does to a plan:
how floating-point numbers round, the feasibility and integrality tolerances of HiGHS and SCIP,
why a tolerance is worth more money in some units than in others, how to measure a model's
coefficient ranges and rescale it without changing its plan, and which lines of a solver log say
that a model's numbers cannot be trusted.

## Contents

1. [Floating point, tolerances, and why 1e-6 matters](README_10.1.1.md)
2. [Coefficient ranges and scaling](README_10.1.2.md)
3. [Spotting numerical trouble in a log](README_10.1.3.md)
