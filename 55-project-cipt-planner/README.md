# 14.2. Growing the CIPT Planner

One project, the CIPT planner (Capital Investment Planning Tool), grown from a one-budget selection
into a planning system, one planner request per lesson: years and cash flows, the business rules,
value by start year and risk, a frontier between the two goals, diagnostics that name the rules,
scenarios stored with their snapshots, and the checks that make a run trustworthy at scale.

The project is kept as complete snapshots in `steps/`: `steps/00` is the starting skeleton and
`steps/NN` is the project after lesson 14.2.NN. Each snapshot is a package `cipt` with its tests
and a demo export, and runs on its own (`python -m pytest -q tests`, `python -m cipt
data/demo.json`). Its `main.py` plans the demo export from any working directory and prints the
report kept in its `expected/report.txt`. The data is GridCap, the course's fictional utility.

## Contents

1. [The first request: fund projects within one budget](README_14.2.1.md)
2. [Many years: start years, windows and cash-flow spreading](README_14.2.2.md)
3. [Business rules: must-dos, bundles, parents and alternatives](README_14.2.3.md)
4. [Value: NPV by start year and risk reduction](README_14.2.4.md)
5. [Two goals: risk against NPV](README_14.2.5.md)
6. [Why it failed, why it was deferred: a diagnostics layer](README_14.2.6.md)
7. [Scenarios, overrides and snapshots](README_14.2.7.md)
8. [Trust at scale: determinism harness, golden tests, warm starts](README_14.2.8.md)
