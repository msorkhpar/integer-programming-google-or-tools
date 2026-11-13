# 14.3. Project: Transformer Fleet Renewal

One project, grown one requirement at a time. It starts as the asset team's worst-first list for
this year's budget, becomes a one-year knapsack model, then a ten-year plan valued with Weibull
failure curves, then a plan that respects substation outages, regional crews, lead times and spare
units. At 5,000 transformers it is measured, rebuilt for scale, given a stronger formulation and a
rolling horizon, planned across uncertain failure curves, and handed off as a tested package with a
report for finance.

The fleets are invented. They belong to GridCap, the course's fictional utility, and come from a
seeded generator in the project (`renewal/fleet.py`); no number in them is a real utility's.

## How the Project Is Kept

The project lives in complete snapshots under [`steps/`](steps): `steps/00` is the skeleton before
the first lesson, and `steps/NN` is the project after lesson NN of this module. Each snapshot is a
package (`renewal/`) with its tests (`tests/`), and runs on its own:

```text
cd steps/04 && python3 -m pytest && python3 -m renewal
```

Each snapshot's `main.py` plans a tiny fleet, 25 units drawn from seed 56, from any working
directory, and prints the report kept in its `expected/report.txt`. Each lesson's project practice
starts from the snapshot before the lesson and is graded by the tests of the snapshot after it and
by that report.

Each lesson shows its change as diffs between two snapshots, and the output of the new tests on the
code before the change and after it. Each snapshot also carries the next lesson's new names as stubs
(marked `Stub:`), so the code before a change always imports, and every new test fails on an
assertion rather than an import error.

## Contents

1. [The first request: replace the worst transformers, and why ranking is not enough](README_14.3.1.md)
2. [A ten-year budget and Weibull failure risk](README_14.3.2.md)
3. [Substation bundles and outage coordination](README_14.3.3.md)
4. [Crews, lead times and spare units](README_14.3.4.md)
5. [From 500 to 5,000 transformers: building the model at scale](README_14.3.5.md)
6. [Too slow: a stronger formulation and a rolling horizon](README_14.3.6.md)
7. [Uncertain failure curves: scenarios and what changes](README_14.3.7.md)
8. [Handoff: tests, packaging and a report for finance](README_14.3.8.md)
