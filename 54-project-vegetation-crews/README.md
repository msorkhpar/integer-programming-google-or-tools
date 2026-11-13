# 14.1. Project: Vegetation Crew Planner

One project, grown one requirement at a time: GridCap's vegetation crew planner starts as a knapsack
that picks the circuits to trim within a budget, and becomes a CP-SAT crew scheduler with growing risk,
access windows, crews' time off, planner overrides, explanations of infeasible seasons, repeatable
runs with golden records, and an HTTP service that keeps its plans in SQLite. Each lesson shows every
changed file before and after, the formulation before and after, the tests the requirement adds and
how they fail on the old code, and what the step did to the code's size and style.

The project lives in complete snapshots: `steps/00` is the starting skeleton and `steps/NN` the
project after lesson 14.1.NN. Each runs on its own (`python -m pytest`, `python -m vegcrew`). Its
`main.py` plans the tiny season from any working directory and prints the report kept in its
`expected/report.txt`. GridCap is fictional, and every season is generated from a seed by the
project's own generator.

## Contents

1. [The first request: which circuits to trim this year](README_14.1.1.md)
2. [Crews and months: capacity over time](README_14.1.2.md)
3. [A trim takes weeks on one crew: from MILP to CP-SAT intervals](README_14.1.3.md)
4. [Risk grows while a circuit waits: the objective changes](README_14.1.4.md)
5. [Weather and access windows: calendars and optional work](README_14.1.5.md)
6. [Planner overrides and why a plan failed](README_14.1.6.md)
7. [The same plan every run: determinism and regression tests](README_14.1.7.md)
8. [From script to service, and what the code became](README_14.1.8.md)
