# Progress

One row per module: `pending`, `in-progress` or `done`. A module is done when it meets the
blueprint's definition of done. Regenerate the table with `python3 scripts/curriculum.py progress`;
change a status by editing its row.

**Done:** 4 / 57 · **In progress:** 41 · **Pending:** 12

## 1. Foundations

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | `01-optimization-mindset` | The optimization mindset | 3 | Core · 65 min | done |
| 02 | `02-math-toolkit` | The math toolkit | 3 | Core · 65 min | done |
| 03 | `03-python-for-optimization` | Python for optimization | 3 | Core · 65 min | done |

## 2. Linear programming

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 04 | `04-lp-modeling` | Modeling linear programs | 3 | Core · 85 min | in-progress |
| 05 | `05-lp-geometry-and-simplex` | LP geometry and the simplex method | 3 | Deep · 65 min | in-progress |
| 06 | `06-duality-and-sensitivity` | Duality and sensitivity | 4 | Core · 85 min | in-progress |
| 07 | `07-lp-solvers-in-practice` | LP solvers in practice | 3 | Survey · 40 min | in-progress |

## 3. Integer programming foundations

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 08 | `08-why-integers` | Why integers | 3 | Core · 65 min | in-progress |
| 09 | `09-branch-and-bound` | Branch and bound | 4 | Deep · 105 min | in-progress |
| 10 | `10-cuts-presolve-heuristics` | Cuts, presolve and heuristics | 4 | Deep · 85 min | in-progress |
| 11 | `11-mip-gap-and-termination` | MIP gap and termination | 3 | Core · 40 min | in-progress |

## 4. Google OR-Tools in depth

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 12 | `12-ortools-landscape` | The OR-Tools landscape | 3 | Survey · 20 min | in-progress |
| 13 | `13-mathopt-core` | MathOpt core | 4 | Core · 85 min | in-progress |
| 14 | `14-mathopt-advanced` | MathOpt advanced | 5 | Core · 105 min | in-progress |
| 15 | `15-cpsat-core` | CP-SAT core | 4 | Core · 85 min | in-progress |
| 16 | `16-cpsat-scheduling` | CP-SAT scheduling | 4 | Deep · 105 min | in-progress |
| 17 | `17-cpsat-tuning-and-diagnostics` | CP-SAT tuning and diagnostics | 4 | Core · 65 min | in-progress |
| 18 | `18-linear-solver-wrapper` | The linear solver wrapper and special-purpose solvers | 4 | Core · 65 min | in-progress |
| 52 | `52-ortools-routing` | OR-Tools routing | 5 | Core · 105 min | in-progress |

## 5. Other modeling frameworks and solvers

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 19 | `19-pyomo` | Pyomo | 4 | Core · 85 min | in-progress |
| 20 | `20-pulp` | PuLP | 2 | Survey · 20 min | in-progress |
| 21 | `21-gurobipy` | gurobipy | 4 | Core · 85 min | in-progress |
| 22 | `22-choosing-a-solver` | Choosing a solver | 4 | Core · 65 min | in-progress |

## 6. Formulation craft

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 23 | `23-binary-logic` | Binary logic | 4 | Core · 85 min | in-progress |
| 24 | `24-big-m-and-indicators` | Big-M and indicators | 4 | Core · 65 min | in-progress |
| 25 | `25-knapsack-and-assignment` | Knapsack and assignment | 3 | Core · 65 min | in-progress |
| 26 | `26-multi-period-timing` | Multi-period timing | 4 | Core · 105 min | done |
| 27 | `27-dependencies-and-groups` | Dependencies and groups | 6 | Core · 125 min | in-progress |
| 28 | `28-piecewise-linear` | Piecewise-linear functions | 4 | Deep · 65 min | in-progress |
| 29 | `29-strong-formulations` | Strong formulations | 4 | Deep · 65 min | in-progress |

## 7. The capital planning domain

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 30 | `30-utility-capital-planning` | Utility capital planning | 4 | Prose · 40 min | in-progress |
| 31 | `31-financial-evaluation` | Financial evaluation | 4 | Core · 65 min | in-progress |
| 32 | `32-asset-risk` | Asset risk | 4 | Core · 85 min | in-progress |
| 33 | `33-value-functions` | Value functions | 4 | Core · 65 min | in-progress |

## 8. Multi-objective optimization

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 34 | `34-weighted-sum` | Weighted sums | 2 | Core · 40 min | in-progress |
| 35 | `35-lexicographic` | Lexicographic objectives | 2 | Core · 40 min | in-progress |
| 36 | `36-epsilon-constraint` | The epsilon-constraint method | 3 | Core · 65 min | in-progress |

## 9. Diagnostics and explainability

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 37 | `37-infeasibility` | Infeasibility | 6 | Core · 125 min | in-progress |
| 38 | `38-sensitivity-for-mip` | Sensitivity for MIP | 4 | Core · 85 min | pending |
| 39 | `39-explaining-decisions` | Explaining decisions | 4 | Core · 85 min | pending |

## 10. Numerics and determinism

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 40 | `40-numerics` | Numerics | 3 | Deep · 40 min | pending |
| 41 | `41-determinism-and-reproducibility` | Determinism and reproducibility | 5 | Core · 85 min | in-progress |

## 11. Performance at scale

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 42 | `42-model-building-at-scale` | Model building at scale | 3 | Core · 65 min | pending |
| 43 | `43-warm-starts-and-tuning` | Warm starts and tuning | 3 | Core · 65 min | in-progress |
| 44 | `44-decomposition-and-heuristics` | Decomposition and heuristics | 5 | Deep · 125 min | in-progress |
| 57 | `57-gpu-acceleration` | GPU acceleration | 6 | Core · 90 min | pending |

## 12. Engineering the optimization service

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 45 | `45-scenario-workflow` | The scenario workflow | 4 | Core · 85 min | in-progress |
| 46 | `46-input-data-quality` | Input data quality | 3 | Core · 40 min | in-progress |
| 47 | `47-testing-optimization-code` | Testing optimization code | 4 | Core · 85 min | in-progress |
| 48 | `48-optimization-api` | The optimization API | 3 | Core · 65 min | in-progress |
| 49 | `49-cloud-deployment` | Cloud deployment | 6 | Core · 105 min | pending |

## 13. Capstone

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 51 | `51-capstone-cipt-lite` | Capstone: CIPT Lite | 6 | Core · 300 min | pending |

## 14. Growing real projects

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 54 | `54-project-vegetation-crews` | Project: vegetation crew planner | 8 | Core · 160 min | pending |
| 55 | `55-project-cipt-planner` | Project: CIPT planner | 8 | Core · 160 min | pending |
| 56 | `56-project-transformer-renewal` | Project: transformer fleet renewal | 8 | Core · 160 min | pending |
| 58 | `58-project-sdd-openspec` | Project: spec-driven development with OpenSpec | 6 | Core · 120 min | pending |

## 15. Mock interviews

| Module | Directory | Title | Lessons | Depth · time | Status |
| --- | --- | --- | --- | --- | --- |
| 53 | `53-mock-interviews` | Mock interviews | 7 | Core · 160 min | pending |

