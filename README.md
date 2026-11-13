# Integer Programming with Python and Google OR-Tools

A self-study course that takes a software engineer who writes basic Python from "what is an
optimization model?" to a tested, explainable, deployable capital-planning MILP service.

To run the course on your machine with Docker, see [`RUNNING.md`](RUNNING.md).

Every lesson works on **GridCap**, the capital portfolio of a fictional utility, generated from a
seed (see [`00-base`](00-base/README.md)). GridCap is invented: it describes no real company.

The main stack is Google OR-Tools (MathOpt for LP and MILP, CP-SAT for logic and scheduling) with
HiGHS as the default solver, plus OR-Tools' routing library and its graph, flow, assignment and
packing solvers. The course also teaches Pyomo, PuLP, gurobipy (on its free size-limited
license), SCIP through MathOpt, pandas, pytest, Hypothesis, FastAPI, and boto3 tested against moto.

## How a lesson works

Each lesson opens with a GridCap problem, states its rules as headings, and shows only code that
ran, with the output it printed. It ends with a short quiz, and its practices sit right after the
section they test. A lesson is as long as its concept needs. Each section ends with an optional
**Going deeper** part: a second explanation, extra readings and longer Stretch practices.

## Sources

The OR-Tools documentation and its samples are the course's primary source: lessons teach the API
the way [developers.google.com/optimization](https://developers.google.com/optimization) does, and
many examples are adapted from the
[OR-Tools samples](https://github.com/google/or-tools/tree/stable/ortools) (Apache-2.0), each marked
with where it came from. Every lesson ends its Reference section with a **Further reading** line that
cites the OR-Tools pages and the other sources it was written from.

The full table of contents, written or not, is in [`docs/COURSE_MAP.md`](docs/COURSE_MAP.md).

## Running the examples

```sh
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install --no-index --require-hashes -r <toolchain>/profiles/optimization/requirements.txt
python3 -m pytest 00-base 01-optimization-mindset
```

The versions are pinned in [`docs/TOOLCHAIN.md`](docs/TOOLCHAIN.md).

## Curriculum

<!-- curriculum:start -->

1. Foundations

- [1.1. The optimization mindset](01-optimization-mindset/README.md)
    - [1.1.1. Decisions, objectives and constraints: turning a planner's question into a model](01-optimization-mindset/README_1.1.1.md)
    - [1.1.2. Predictive vs. prescriptive: where PoF/RUL predictions stop and optimization starts](01-optimization-mindset/README_1.1.2.md)
    - [1.1.3. The problem zoo: LP, MILP, CP, NLP and how to pick](01-optimization-mindset/README_1.1.3.md)
- [1.2. The math toolkit](02-math-toolkit/README.md)
    - [1.2.1. Vectors, matrices and Ax ≤ b in NumPy](02-math-toolkit/README_1.2.1.md)
    - [1.2.2. Sparse model matrices and why solvers rely on sparsity](02-math-toolkit/README_1.2.2.md)
    - [1.2.3. Convex sets, polyhedra and extreme points](02-math-toolkit/README_1.2.3.md)
- [1.3. Python for optimization](03-python-for-optimization/README.md)
    - [1.3.1. Preparing model input with pandas](03-python-for-optimization/README_1.3.1.md)
    - [1.3.2. Typed inputs with dataclasses and pydantic](03-python-for-optimization/README_1.3.2.md)
    - [1.3.3. Testing numerical code with pytest: tolerances, fixtures, parametrize](03-python-for-optimization/README_1.3.3.md)

2. Linear programming

- [2.1. Modeling linear programs](04-lp-modeling/README.md)
    - [2.1.1. Your first LP: splitting a maintenance budget across programs](04-lp-modeling/README_2.1.1.md)
    - [2.1.2. Standard form, slack and surplus](04-lp-modeling/README_2.1.2.md)
    - [2.1.3. LP patterns: blending, flows, multi-period carry-over](04-lp-modeling/README_2.1.3.md)
- [2.2. LP geometry and the simplex method](05-lp-geometry-and-simplex/README.md)
    - [2.2.1. Solving a 2-variable LP by picture](05-lp-geometry-and-simplex/README_2.2.1.md)
    - [2.2.2. Simplex as walking between vertices (a tiny tableau implementation)](05-lp-geometry-and-simplex/README_2.2.2.md)
    - [2.2.3. Infeasible, unbounded and degenerate LPs](05-lp-geometry-and-simplex/README_2.2.3.md)
- [2.3. Duality and sensitivity](06-duality-and-sensitivity/README.md)
    - [2.3.1. The dual LP and what its variables price](06-duality-and-sensitivity/README_2.3.1.md)
    - [2.3.2. Weak and strong duality, complementary slackness](06-duality-and-sensitivity/README_2.3.2.md)
    - [2.3.3. Shadow prices, reduced costs and ranging from a solver](06-duality-and-sensitivity/README_2.3.3.md)
    - [2.3.4. Explaining a dual value to a finance partner](06-duality-and-sensitivity/README_2.3.4.md)
- [2.4. LP solvers in practice](07-lp-solvers-in-practice/README.md)
    - [2.4.1. Simplex, interior point and PDLP: GLOP, HiGHS, PDLP](07-lp-solvers-in-practice/README_2.4.1.md)
    - [2.4.2. Reading an LP solver log](07-lp-solvers-in-practice/README_2.4.2.md)
    - [2.4.3. Re-solving after the data changes](07-lp-solvers-in-practice/README_2.4.3.md)

3. Integer programming foundations

- [3.1. Why integers](08-why-integers/README.md)
    - [3.1.1. Yes/no decisions, and why rounding an LP fails](08-why-integers/README_3.1.1.md)
    - [3.1.2. The integrality gap, measured on GridCap](08-why-integers/README_3.1.2.md)
    - [3.1.3. Why MILP is hard: combinatorial growth in numbers](08-why-integers/README_3.1.3.md)
- [3.2. Branch and bound](09-branch-and-bound/README.md)
    - [3.2.1. Branching on a fractional variable](09-branch-and-bound/README_3.2.1.md)
    - [3.2.2. Bounds, incumbents and pruning](09-branch-and-bound/README_3.2.2.md)
    - [3.2.3. Node and variable selection](09-branch-and-bound/README_3.2.3.md)
    - [3.2.4. A knapsack branch-and-bound in 116 lines](09-branch-and-bound/README_3.2.4.md)
- [3.3. Cuts, presolve and heuristics](10-cuts-presolve-heuristics/README.md)
    - [3.3.1. Cutting planes: Gomory and cover cuts by hand](10-cuts-presolve-heuristics/README_3.3.1.md)
    - [3.3.2. Presolve: what the solver removes first](10-cuts-presolve-heuristics/README_3.3.2.md)
    - [3.3.3. Primal heuristics: rounding, diving, RINS](10-cuts-presolve-heuristics/README_3.3.3.md)
    - [3.3.4. Reading a full MIP log line by line](10-cuts-presolve-heuristics/README_3.3.4.md)
- [3.4. MIP gap and termination](11-mip-gap-and-termination/README.md)
    - [3.4.1. Best bound, incumbent, absolute and relative gap](11-mip-gap-and-termination/README_3.4.1.md)
    - [3.4.2. Stopping on gap, time, nodes or solution count](11-mip-gap-and-termination/README_3.4.2.md)
    - [3.4.3. What "optimal at 0.01%" means on a $2B portfolio](11-mip-gap-and-termination/README_3.4.3.md)

4. Google OR-Tools in depth

- [4.1. The OR-Tools landscape](12-ortools-landscape/README.md)
    - [4.1.1. What's in OR-Tools: MathOpt, CP-SAT, linear solver wrapper, routing, graph](12-ortools-landscape/README_4.1.1.md)
    - [4.1.2. Versions and the backends that ship with it](12-ortools-landscape/README_4.1.2.md)
    - [4.1.3. Choosing an API for a problem](12-ortools-landscape/README_4.1.3.md)
- [4.2. MathOpt core](13-mathopt-core/README.md)
    - [4.2.1. Model, variables, constraints, objective](13-mathopt-core/README_4.2.1.md)
    - [4.2.2. Reading `SolveResult`: termination, primal and dual solutions, statistics](13-mathopt-core/README_4.2.2.md)
    - [4.2.3. Switching solvers: HiGHS, SCIP, CP-SAT, GLOP, Gurobi](13-mathopt-core/README_4.2.3.md)
    - [4.2.4. Common vs. solver-specific parameters, and what each solver rejects](13-mathopt-core/README_4.2.4.md)
- [4.3. MathOpt advanced](14-mathopt-advanced/README.md)
    - [4.3.1. Indicator constraints](14-mathopt-advanced/README_4.3.1.md)
    - [4.3.2. Prioritized objectives with `add_auxiliary_objective`](14-mathopt-advanced/README_4.3.2.md)
    - [4.3.3. Solution hints and `ModelSolveParameters`](14-mathopt-advanced/README_4.3.3.md)
    - [4.3.4. Incremental solving: edit the model, re-solve](14-mathopt-advanced/README_4.3.4.md)
    - [4.3.5. Callbacks and `compute_infeasible_subsystem`](14-mathopt-advanced/README_4.3.5.md)
- [4.4. CP-SAT core](15-cpsat-core/README.md)
    - [4.4.1. Integer and Boolean variables, linear constraints over integers](15-cpsat-core/README_4.4.1.md)
    - [4.4.2. Native logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf`](15-cpsat-core/README_4.4.2.md)
    - [4.4.3. Objectives, integer scaling and solution callbacks](15-cpsat-core/README_4.4.3.md)
    - [4.4.4. When CP-SAT beats MIP, and when it doesn't](15-cpsat-core/README_4.4.4.md)
- [4.5. CP-SAT scheduling](16-cpsat-scheduling/README.md)
    - [4.5.1. Interval variables and `NoOverlap`](16-cpsat-scheduling/README_4.5.1.md)
    - [4.5.2. Cumulative resources: crews and outage windows](16-cpsat-scheduling/README_4.5.2.md)
    - [4.5.3. Element, table and allowed-assignment constraints](16-cpsat-scheduling/README_4.5.3.md)
    - [4.5.4. Scheduling vegetation crews across circuits](16-cpsat-scheduling/README_4.5.4.md)
- [4.6. CP-SAT tuning and diagnostics](17-cpsat-tuning-and-diagnostics/README.md)
    - [4.6.1. Workers, search strategies and LNS](17-cpsat-tuning-and-diagnostics/README_4.6.1.md)
    - [4.6.2. Hints, assumptions and `SufficientAssumptionsForInfeasibility`](17-cpsat-tuning-and-diagnostics/README_4.6.2.md)
    - [4.6.3. Deterministic time, seeds and reproducible runs](17-cpsat-tuning-and-diagnostics/README_4.6.3.md)
    - [4.6.4. Reading the CP-SAT log](17-cpsat-tuning-and-diagnostics/README_4.6.4.md)
- [4.7. The linear solver wrapper and special-purpose solvers](18-linear-solver-wrapper/README.md)
    - [4.7.1. Reading pywraplp code](18-linear-solver-wrapper/README_4.7.1.md)
    - [4.7.2. Migrating a pywraplp model to MathOpt](18-linear-solver-wrapper/README_4.7.2.md)
    - [4.7.3. Graph and flow solvers: `SimpleMaxFlow` and `SimpleMinCostFlow`](18-linear-solver-wrapper/README_4.7.3.md)
    - [4.7.4. Special-purpose solvers: `LinearSumAssignment`, `KnapsackSolver` and bin packing](18-linear-solver-wrapper/README_4.7.4.md)
- [4.8. OR-Tools routing](52-ortools-routing/README.md)
    - [4.8.1. The routing model: index manager, transit callbacks and the TSP](52-ortools-routing/README_4.8.1.md)
    - [4.8.2. Vehicles, capacities and dimensions (CVRP)](52-ortools-routing/README_4.8.2.md)
    - [4.8.3. Time windows and service times (VRPTW)](52-ortools-routing/README_4.8.3.md)
    - [4.8.4. Optional visits with penalties, and pickup and delivery](52-ortools-routing/README_4.8.4.md)
    - [4.8.5. First-solution strategies, local search and search limits](52-ortools-routing/README_4.8.5.md)

5. Other modeling frameworks and solvers

- [5.1. Pyomo](19-pyomo/README.md)
    - [5.1.1. Concrete models with indexed Sets, Params, Vars and Constraints](19-pyomo/README_5.1.1.md)
    - [5.1.2. Solving with HiGHS and reading results](19-pyomo/README_5.1.2.md)
    - [5.1.3. Pyomo.GDP: disjunctions, big-M and hull transformations](19-pyomo/README_5.1.3.md)
    - [5.1.4. Piecewise functions and the IIS tools](19-pyomo/README_5.1.4.md)
- [5.2. PuLP](20-pulp/README.md)
    - [5.2.1. A PuLP model end to end with CBC](20-pulp/README_5.2.1.md)
    - [5.2.2. Reading PuLP code you inherit](20-pulp/README_5.2.2.md)
- [5.3. gurobipy](21-gurobipy/README.md)
    - [5.3.1. Models, attributes and the matrix API](21-gurobipy/README_5.3.1.md)
    - [5.3.2. Duals, reduced costs and sensitivity attributes](21-gurobipy/README_5.3.2.md)
    - [5.3.3. `computeIIS`, `feasRelax` and `setObjectiveN`](21-gurobipy/README_5.3.3.md)
    - [5.3.4. Licenses: size-limited, academic, and cloud/container (WLS)](21-gurobipy/README_5.3.4.md)
- [5.4. Choosing a solver](22-choosing-a-solver/README.md)
    - [5.4.1. The landscape: Gurobi, CPLEX, Xpress, HiGHS, SCIP, CBC, CP-SAT](22-choosing-a-solver/README_5.4.1.md)
    - [5.4.2. Honest benchmarking: instance sets, seeds, time-to-gap, shifted geometric mean](22-choosing-a-solver/README_5.4.2.md)
    - [5.4.3. License cost and fit for containers](22-choosing-a-solver/README_5.4.3.md)
    - [5.4.4. Writing a solver recommendation](22-choosing-a-solver/README_5.4.4.md)

6. Formulation craft

- [6.1. Binary logic](23-binary-logic/README.md)
    - [6.1.1. Binary selection and counting constraints](23-binary-logic/README_6.1.1.md)
    - [6.1.2. AND, OR, NOT, XOR and implication as linear constraints](23-binary-logic/README_6.1.2.md)
    - [6.1.3. At-least-k, at-most-k, exactly-k](23-binary-logic/README_6.1.3.md)
    - [6.1.4. Linearizing binary × binary and binary × bounded continuous](23-binary-logic/README_6.1.4.md)
- [6.2. Big-M and indicators](24-big-m-and-indicators/README.md)
    - [6.2.1. Deriving big-M from bounds](24-big-m-and-indicators/README_6.2.1.md)
    - [6.2.2. What a loose M does to the LP bound and to numerics](24-big-m-and-indicators/README_6.2.2.md)
    - [6.2.3. Indicator constraints vs. big-M](24-big-m-and-indicators/README_6.2.3.md)
    - [6.2.4. Disjunctions: big-M vs. hull](24-big-m-and-indicators/README_6.2.4.md)
- [6.3. Knapsack and assignment](25-knapsack-and-assignment/README.md)
    - [6.3.1. 0-1 and multi-dimensional knapsack](25-knapsack-and-assignment/README_6.3.1.md)
    - [6.3.2. Multiple knapsack and generalized assignment](25-knapsack-and-assignment/README_6.3.2.md)
    - [6.3.3. Cover inequalities that tighten budget rows](25-knapsack-and-assignment/README_6.3.3.md)
- [6.4. Multi-period timing](26-multi-period-timing/README.md)
    - [6.4.1. Start-time variables x(i,t) and timing windows](26-multi-period-timing/README_6.4.1.md)
    - [6.4.2. Cash-flow spreading across years](26-multi-period-timing/README_6.4.2.md)
    - [6.4.3. Aggregated vs. cumulative (disaggregated) forms](26-multi-period-timing/README_6.4.3.md)
    - [6.4.4. Carry-over budgets and multi-year caps](26-multi-period-timing/README_6.4.4.md)
- [6.5. Dependencies and groups](27-dependencies-and-groups/README.md)
    - [6.5.1. Must-do vs. discretionary planning groups](27-dependencies-and-groups/README_6.5.1.md)
    - [6.5.2. Parent-child bundles and all-or-nothing](27-dependencies-and-groups/README_6.5.2.md)
    - [6.5.3. Mutually exclusive alternatives (repair vs. replace)](27-dependencies-and-groups/README_6.5.3.md)
    - [6.5.4. Precedence with lags](27-dependencies-and-groups/README_6.5.4.md)
    - [6.5.5. Jurisdictional and portfolio minimum/maximum spend](27-dependencies-and-groups/README_6.5.5.md)
    - [6.5.6. Manual overrides as fixed bounds](27-dependencies-and-groups/README_6.5.6.md)
- [6.6. Piecewise-linear functions](28-piecewise-linear/README.md)
    - [6.6.1. Convex piecewise costs without binaries](28-piecewise-linear/README_6.6.1.md)
    - [6.6.2. The lambda (SOS2-style) formulation built from binaries](28-piecewise-linear/README_6.6.2.md)
    - [6.6.3. Incremental and logarithmic formulations](28-piecewise-linear/README_6.6.3.md)
    - [6.6.4. Lifecycle value curves for asset renewal](28-piecewise-linear/README_6.6.4.md)
- [6.7. Strong formulations](29-strong-formulations/README.md)
    - [6.7.1. Comparing formulations by their LP bound](29-strong-formulations/README_6.7.1.md)
    - [6.7.2. Bound tightening and valid inequalities](29-strong-formulations/README_6.7.2.md)
    - [6.7.3. Symmetry and how to break it](29-strong-formulations/README_6.7.3.md)
    - [6.7.4. Case study: reformulating GridCap medium](29-strong-formulations/README_6.7.4.md)

7. The capital planning domain

- [7.1. Utility capital planning](30-utility-capital-planning/README.md)
    - [7.1.1. How a utility plans capital: programs, portfolios, rate cases](30-utility-capital-planning/README_7.1.1.md)
    - [7.1.2. Transmission, distribution and vegetation investments](30-utility-capital-planning/README_7.1.2.md)
    - [7.1.3. The planning cycle: Initial, Pre-Opt, Post-Opt, Budget Lock](30-utility-capital-planning/README_7.1.3.md)
    - [7.1.4. What planners, finance and regulators each need from the optimizer](30-utility-capital-planning/README_7.1.4.md)
- [7.2. Financial evaluation](31-financial-evaluation/README.md)
    - [7.2.1. Present value, NPV and discount rates](31-financial-evaluation/README_7.2.1.md)
    - [7.2.2. Escalation; real vs. nominal dollars](31-financial-evaluation/README_7.2.2.md)
    - [7.2.3. Annuities, lifecycle cost, equivalent annual cost](31-financial-evaluation/README_7.2.3.md)
    - [7.2.4. Precomputing NPV coefficients by start year](31-financial-evaluation/README_7.2.4.md)
- [7.3. Asset risk](32-asset-risk/README.md)
    - [7.3.1. Probability of failure and hazard curves (Weibull)](32-asset-risk/README_7.3.1.md)
    - [7.3.2. Remaining useful life: what an ML model actually hands you](32-asset-risk/README_7.3.2.md)
    - [7.3.3. Consequence of failure and risk = PoF × CoF](32-asset-risk/README_7.3.3.md)
    - [7.3.4. Risk reduction from an intervention, year by year](32-asset-risk/README_7.3.4.md)
- [7.4. Value functions](33-value-functions/README.md)
    - [7.4.1. Benefit measures: reliability, safety, environmental, financial](33-value-functions/README_7.4.1.md)
    - [7.4.2. Normalizing different units](33-value-functions/README_7.4.2.md)
    - [7.4.3. Weights, swing weighting and stakeholder buy-in](33-value-functions/README_7.4.3.md)
    - [7.4.4. Building the CIPT value function](33-value-functions/README_7.4.4.md)

8. Multi-objective optimization

- [8.1. Weighted sums](34-weighted-sum/README.md)
    - [8.1.1. Weighted sums and what the weights really mean](34-weighted-sum/README_8.1.1.md)
    - [8.1.2. Supported and unsupported Pareto points](34-weighted-sum/README_8.1.2.md)
- [8.2. Lexicographic objectives](35-lexicographic/README.md)
    - [8.2.1. Hierarchical objectives with tolerances](35-lexicographic/README_8.2.1.md)
    - [8.2.2. Three implementations: auxiliary objectives in MathOpt, `setObjectiveN` in gurobipy, and a manual two-pass solve](35-lexicographic/README_8.2.2.md)
- [8.3. The epsilon-constraint method](36-epsilon-constraint/README.md)
    - [8.3.1. The ε-constraint method](36-epsilon-constraint/README_8.3.1.md)
    - [8.3.2. AUGMECON: avoiding weakly efficient points](36-epsilon-constraint/README_8.3.2.md)
    - [8.3.3. Generating a frontier and presenting it to planners](36-epsilon-constraint/README_8.3.3.md)

9. Diagnostics and explainability

- [9.1. Infeasibility](37-infeasibility/README.md)
    - [9.1.1. Infeasible, unbounded, or the solver can't tell](37-infeasibility/README_9.1.1.md)
    - [9.1.2. Validating inputs before the solve](37-infeasibility/README_9.1.2.md)
    - [9.1.3. IIS with MathOpt, gurobipy and Pyomo](37-infeasibility/README_9.1.3.md)
    - [9.1.4. Elastic constraints and feasibility relaxation](37-infeasibility/README_9.1.4.md)
    - [9.1.5. CP-SAT assumptions as a conflict finder](37-infeasibility/README_9.1.5.md)
    - [9.1.6. Turning an IIS into a planner message](37-infeasibility/README_9.1.6.md)
- [9.2. Sensitivity for MIP](38-sensitivity-for-mip/README.md)
    - [9.2.1. Why a MILP has no duals](38-sensitivity-for-mip/README_9.2.1.md)
    - [9.2.2. Fixed-integer LP duals, and when they mean something](38-sensitivity-for-mip/README_9.2.2.md)
    - [9.2.3. Parametric analysis: the budget-value frontier](38-sensitivity-for-mip/README_9.2.3.md)
    - [9.2.4. The marginal value of the next dollar](38-sensitivity-for-mip/README_9.2.4.md)
- [9.3. Explaining decisions](39-explaining-decisions/README.md)
    - [9.3.1. A binding-constraints report](39-explaining-decisions/README_9.3.1.md)
    - [9.3.2. Why selected, why deferred: forcing in and out](39-explaining-decisions/README_9.3.2.md)
    - [9.3.3. Scenario diffs: selected, deferred, shifted](39-explaining-decisions/README_9.3.3.md)
    - [9.3.4. Writing results for planners, finance and auditors](39-explaining-decisions/README_9.3.4.md)

10. Numerics and determinism

- [10.1. Numerics](40-numerics/README.md)
    - [10.1.1. Floating point, tolerances, and why 1e-6 matters](40-numerics/README_10.1.1.md)
    - [10.1.2. Coefficient ranges and scaling](40-numerics/README_10.1.2.md)
    - [10.1.3. Spotting numerical trouble in a log](40-numerics/README_10.1.3.md)
- [10.2. Determinism and reproducibility](41-determinism-and-reproducibility/README.md)
    - [10.2.1. Where nondeterminism comes from: threads, time limits, ties](41-determinism-and-reproducibility/README_10.2.1.md)
    - [10.2.2. Seeds, threads and deterministic work limits, solver by solver](41-determinism-and-reproducibility/README_10.2.2.md)
    - [10.2.3. Alternative optima and deterministic tie-breaking](41-determinism-and-reproducibility/README_10.2.3.md)
    - [10.2.4. Versioned input snapshots, pinned solvers and run manifests](41-determinism-and-reproducibility/README_10.2.4.md)
    - [10.2.5. Building the deterministic run harness](41-determinism-and-reproducibility/README_10.2.5.md)

11. Performance at scale

- [11.1. Model building at scale](42-model-building-at-scale/README.md)
    - [11.1.1. Measuring build time vs. solve time](42-model-building-at-scale/README_11.1.1.md)
    - [11.1.2. Vectorized model building from DataFrames](42-model-building-at-scale/README_11.1.2.md)
    - [11.1.3. A generator for 10,000-project portfolios](42-model-building-at-scale/README_11.1.3.md)
- [11.2. Warm starts and tuning](43-warm-starts-and-tuning/README.md)
    - [11.2.1. MIP starts from last cycle's plan](43-warm-starts-and-tuning/README_11.2.1.md)
    - [11.2.2. The parameters that matter: presolve, cuts, heuristics, focus](43-warm-starts-and-tuning/README_11.2.2.md)
    - [11.2.3. Automated tuning, and how not to overfit it](43-warm-starts-and-tuning/README_11.2.3.md)
- [11.3. Decomposition and heuristics](44-decomposition-and-heuristics/README.md)
    - [11.3.1. Lagrangian relaxation and subgradient optimization](44-decomposition-and-heuristics/README_11.3.1.md)
    - [11.3.2. Benders decomposition](44-decomposition-and-heuristics/README_11.3.2.md)
    - [11.3.3. Logic-based Benders](44-decomposition-and-heuristics/README_11.3.3.md)
    - [11.3.4. Column generation in one worked example](44-decomposition-and-heuristics/README_11.3.4.md)
    - [11.3.5. Rolling horizon and LNS heuristics](44-decomposition-and-heuristics/README_11.3.5.md)
- [11.4. GPU acceleration](57-gpu-acceleration/README.md)
    - [11.4.1. Why first-order LP methods suit a GPU: PDHG and PDLP](57-gpu-acceleration/README_11.4.1.md)
    - [11.4.2. Detecting a GPU, with a CPU fallback that gives the same answer](57-gpu-acceleration/README_11.4.2.md)
    - [11.4.3. PDLP on CPU vs. GPU: a measured comparison with HiGHS (cuPDLP-C) and OR-Tools](57-gpu-acceleration/README_11.4.3.md)
    - [11.4.4. Determinism on a GPU: what repeats, what doesn't, and what the manifest records](57-gpu-acceleration/README_11.4.4.md)
    - [11.4.5. MIP on a GPU: what cuOpt accelerates and why branch-and-bound stays on the CPU](57-gpu-acceleration/README_11.4.5.md)
    - [11.4.6. One run policy for threads, workers and the GPU](57-gpu-acceleration/README_11.4.6.md)

12. Engineering the optimization service

- [12.1. The scenario workflow](45-scenario-workflow/README.md)
    - [12.1.1. Scenarios as data: create, copy, optimize](45-scenario-workflow/README_12.1.1.md)
    - [12.1.2. Manual overrides as bounds, with an audit trail](45-scenario-workflow/README_12.1.2.md)
    - [12.1.3. Planning-cycle states and locking](45-scenario-workflow/README_12.1.3.md)
    - [12.1.4. Storing scenarios and results in SQLite](45-scenario-workflow/README_12.1.4.md)
- [12.2. Input data quality](46-input-data-quality/README.md)
    - [12.2.1. Schemas for model inputs](46-input-data-quality/README_12.2.1.md)
    - [12.2.2. Data-quality checks that prevent infeasibility](46-input-data-quality/README_12.2.2.md)
    - [12.2.3. Versioned snapshots and content hashes](46-input-data-quality/README_12.2.3.md)
- [12.3. Testing optimization code](47-testing-optimization-code/README.md)
    - [12.3.1. Unit-testing one constraint at a time](47-testing-optimization-code/README_12.3.1.md)
    - [12.3.2. Property-based tests with Hypothesis](47-testing-optimization-code/README_12.3.2.md)
    - [12.3.3. Golden datasets and regression tests](47-testing-optimization-code/README_12.3.3.md)
    - [12.3.4. Determinism tests and back-testing against history](47-testing-optimization-code/README_12.3.4.md)
- [12.4. The optimization API](48-optimization-api/README.md)
    - [12.4.1. A REST API with FastAPI](48-optimization-api/README_12.4.1.md)
    - [12.4.2. Long solves: submit, poll, fetch](48-optimization-api/README_12.4.2.md)
    - [12.4.3. Result schemas planners can consume](48-optimization-api/README_12.4.3.md)
- [12.5. Cloud deployment](49-cloud-deployment/README.md)
    - [12.5.1. Containerizing a solver service](49-cloud-deployment/README_12.5.1.md)
    - [12.5.2. AWS Batch on Fargate, Step Functions and Lambda: who does what](49-cloud-deployment/README_12.5.2.md)
    - [12.5.3. S3 and a local SQLite file for snapshots and results](49-cloud-deployment/README_12.5.3.md)
    - [12.5.4. Testing AWS code against moto](49-cloud-deployment/README_12.5.4.md)
    - [12.5.5. Terraform for the optimization stack](49-cloud-deployment/README_12.5.5.md)
    - [12.5.6. CI/CD with GitHub Actions](49-cloud-deployment/README_12.5.6.md)

13. Capstone

- [13.1. Capstone: CIPT Lite](51-capstone-cipt-lite/README.md)
    - [13.1.1. Data: load, validate and snapshot the portfolio](51-capstone-cipt-lite/README_13.1.1.md)
    - [13.1.2. Model: multi-period selection with all section 6 rules](51-capstone-cipt-lite/README_13.1.2.md)
    - [13.1.3. Value: NPV by start year, risk reduction from PoF/RUL, weighted value](51-capstone-cipt-lite/README_13.1.3.md)
    - [13.1.4. Diagnostics: pre-solve checks, IIS message, why-deferred report](51-capstone-cipt-lite/README_13.1.4.md)
    - [13.1.5. Trust: determinism harness, Hypothesis properties, golden test, warm start](51-capstone-cipt-lite/README_13.1.5.md)
    - [13.1.6. Service: FastAPI job API, moto-tested S3 store, Pareto frontier endpoint](51-capstone-cipt-lite/README_13.1.6.md)

14. Growing real projects

- [14.1. Project: vegetation crew planner](54-project-vegetation-crews/README.md)
    - [14.1.1. The first request: which circuits to trim this year](54-project-vegetation-crews/README_14.1.1.md)
    - [14.1.2. Crews and months: capacity over time](54-project-vegetation-crews/README_14.1.2.md)
    - [14.1.3. A trim takes weeks on one crew: from MILP to CP-SAT intervals](54-project-vegetation-crews/README_14.1.3.md)
    - [14.1.4. Risk grows while a circuit waits: the objective changes](54-project-vegetation-crews/README_14.1.4.md)
    - [14.1.5. Weather and access windows: calendars and optional work](54-project-vegetation-crews/README_14.1.5.md)
    - [14.1.6. Planner overrides and why a plan failed](54-project-vegetation-crews/README_14.1.6.md)
    - [14.1.7. The same plan every run: determinism and regression tests](54-project-vegetation-crews/README_14.1.7.md)
    - [14.1.8. From script to service, and what the code became](54-project-vegetation-crews/README_14.1.8.md)
- [14.2. Project: CIPT planner](55-project-cipt-planner/README.md)
    - [14.2.1. The first request: fund projects within one budget](55-project-cipt-planner/README_14.2.1.md)
    - [14.2.2. Many years: start years, windows and cash-flow spreading](55-project-cipt-planner/README_14.2.2.md)
    - [14.2.3. Business rules: must-dos, bundles, parents and alternatives](55-project-cipt-planner/README_14.2.3.md)
    - [14.2.4. Value: NPV by start year and risk reduction](55-project-cipt-planner/README_14.2.4.md)
    - [14.2.5. Two goals: risk against NPV](55-project-cipt-planner/README_14.2.5.md)
    - [14.2.6. Why it failed, why it was deferred: a diagnostics layer](55-project-cipt-planner/README_14.2.6.md)
    - [14.2.7. Scenarios, overrides and snapshots](55-project-cipt-planner/README_14.2.7.md)
    - [14.2.8. Trust at scale: determinism harness, golden tests, warm starts](55-project-cipt-planner/README_14.2.8.md)
- [14.3. Project: transformer fleet renewal](56-project-transformer-renewal/README.md)
    - [14.3.1. The first request: replace the worst transformers, and why ranking is not enough](56-project-transformer-renewal/README_14.3.1.md)
    - [14.3.2. A ten-year budget and Weibull failure risk](56-project-transformer-renewal/README_14.3.2.md)
    - [14.3.3. Substation bundles and outage coordination](56-project-transformer-renewal/README_14.3.3.md)
    - [14.3.4. Crews, lead times and spare units](56-project-transformer-renewal/README_14.3.4.md)
    - [14.3.5. From 500 to 5,000 transformers: building the model at scale](56-project-transformer-renewal/README_14.3.5.md)
    - [14.3.6. Too slow: a stronger formulation and a rolling horizon](56-project-transformer-renewal/README_14.3.6.md)
    - [14.3.7. Uncertain failure curves: scenarios and what changes](56-project-transformer-renewal/README_14.3.7.md)
    - [14.3.8. Handoff: tests, packaging and a report for finance](56-project-transformer-renewal/README_14.3.8.md)
- [14.4. Project: spec-driven development with OpenSpec](58-project-sdd-openspec/README.md)
    - [14.4.1. Baseline specs: write down what the planner already does](58-project-sdd-openspec/README_14.4.1.md)
    - [14.4.2. A regional spend share: the first change from proposal to archive](58-project-sdd-openspec/README_14.4.2.md)
    - [14.4.3. A must-do override that needs a recorded reason](58-project-sdd-openspec/README_14.4.3.md)
    - [14.4.4. Carry-over: a MODIFIED budget rule and a RENAMED requirement](58-project-sdd-openspec/README_14.4.4.md)
    - [14.4.5. Retiring the yearly start cap: a REMOVED requirement](58-project-sdd-openspec/README_14.4.5.md)
    - [14.4.6. Living specs: every scenario traced to a test, every test to a scenario](58-project-sdd-openspec/README_14.4.6.md)

15. Mock interviews

- [15.1. Mock interviews](53-mock-interviews/README.md)
    - [15.1.1. Mock 1: modeling and formulation](53-mock-interviews/README_15.1.1.md)
    - [15.1.2. Mock 2: solvers, OR-Tools and the search](53-mock-interviews/README_15.1.2.md)
    - [15.1.3. Mock 3: value, objectives and trade-offs](53-mock-interviews/README_15.1.3.md)
    - [15.1.4. Mock 4: diagnostics, sensitivity and explanations](53-mock-interviews/README_15.1.4.md)
    - [15.1.5. Mock 5: production, trust and performance](53-mock-interviews/README_15.1.5.md)
    - [15.1.6. Mixed mock A: a technical screen](53-mock-interviews/README_15.1.6.md)
    - [15.1.7. Mixed mock B: an onsite loop](53-mock-interviews/README_15.1.7.md)

<!-- curriculum:end -->
