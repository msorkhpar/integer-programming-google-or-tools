# Course Map

The whole table of contents, generated from `docs/plan/blueprint.md` by
`python3 scripts/curriculum.py map`. A module links to its page once it is written; the README's
curriculum lists only written modules, because StudyForge reads that list.

15 sections, 57 modules, 237 lessons.

## 1. Foundations

- **1.1. [The optimization mindset](../01-optimization-mindset/README.md)** (Core, module 01, done)
    - 1.1.1 Decisions, objectives and constraints: turning a planner's question into a model
    - 1.1.2 Predictive vs. prescriptive: where PoF/RUL predictions stop and optimization starts
    - 1.1.3 The problem zoo: LP, MILP, CP, NLP and how to pick
- **1.2. [The math toolkit](../02-math-toolkit/README.md)** (Core, module 02, done)
    - 1.2.1 Vectors, matrices and Ax ≤ b in NumPy
    - 1.2.2 Sparse model matrices and why solvers rely on sparsity
    - 1.2.3 Convex sets, polyhedra and extreme points
- **1.3. [Python for optimization](../03-python-for-optimization/README.md)** (Core, module 03, done)
    - 1.3.1 Preparing model input with pandas
    - 1.3.2 Typed inputs with dataclasses and pydantic
    - 1.3.3 Testing numerical code with pytest: tolerances, fixtures, parametrize

## 2. Linear programming

- **2.1. [Modeling linear programs](../04-lp-modeling/README.md)** (Core, module 04, in-progress)
    - 2.1.1 Your first LP: splitting a maintenance budget across programs
    - 2.1.2 Standard form, slack and surplus
    - 2.1.3 LP patterns: blending, flows, multi-period carry-over
- **2.2. [LP geometry and the simplex method](../05-lp-geometry-and-simplex/README.md)** (Deep, module 05, in-progress)
    - 2.2.1 Solving a 2-variable LP by picture
    - 2.2.2 Simplex as walking between vertices (a tiny tableau implementation)
    - 2.2.3 Infeasible, unbounded and degenerate LPs
- **2.3. [Duality and sensitivity](../06-duality-and-sensitivity/README.md)** (Core, module 06, in-progress)
    - 2.3.1 The dual LP and what its variables price
    - 2.3.2 Weak and strong duality, complementary slackness
    - 2.3.3 Shadow prices, reduced costs and ranging from a solver
    - 2.3.4 Explaining a dual value to a finance partner
- **2.4. [LP solvers in practice](../07-lp-solvers-in-practice/README.md)** (Survey, module 07, in-progress)
    - 2.4.1 Simplex, interior point and PDLP: GLOP, HiGHS, PDLP
    - 2.4.2 Reading an LP solver log
    - 2.4.3 Re-solving after the data changes

## 3. Integer programming foundations

- **3.1. [Why integers](../08-why-integers/README.md)** (Core, module 08, in-progress)
    - 3.1.1 Yes/no decisions, and why rounding an LP fails
    - 3.1.2 The integrality gap, measured on GridCap
    - 3.1.3 Why MILP is hard: combinatorial growth in numbers
- **3.2. [Branch and bound](../09-branch-and-bound/README.md)** (Deep, module 09, in-progress)
    - 3.2.1 Branching on a fractional variable
    - 3.2.2 Bounds, incumbents and pruning
    - 3.2.3 Node and variable selection
    - 3.2.4 A knapsack branch-and-bound in 116 lines
- **3.3. [Cuts, presolve and heuristics](../10-cuts-presolve-heuristics/README.md)** (Deep, module 10, in-progress)
    - 3.3.1 Cutting planes: Gomory and cover cuts by hand
    - 3.3.2 Presolve: what the solver removes first
    - 3.3.3 Primal heuristics: rounding, diving, RINS
    - 3.3.4 Reading a full MIP log line by line
- **3.4. [MIP gap and termination](../11-mip-gap-and-termination/README.md)** (Core, module 11, in-progress)
    - 3.4.1 Best bound, incumbent, absolute and relative gap
    - 3.4.2 Stopping on gap, time, nodes or solution count
    - 3.4.3 What "optimal at 0.01%" means on a $2B portfolio

## 4. Google OR-Tools in depth

- **4.1. [The OR-Tools landscape](../12-ortools-landscape/README.md)** (Survey, module 12, in-progress)
    - 4.1.1 What's in OR-Tools: MathOpt, CP-SAT, linear solver wrapper, routing, graph
    - 4.1.2 Versions and the backends that ship with it
    - 4.1.3 Choosing an API for a problem
- **4.2. [MathOpt core](../13-mathopt-core/README.md)** (Core, module 13, in-progress)
    - 4.2.1 Model, variables, constraints, objective
    - 4.2.2 Reading `SolveResult`: termination, primal and dual solutions, statistics
    - 4.2.3 Switching solvers: HiGHS, SCIP, CP-SAT, GLOP, Gurobi
    - 4.2.4 Common vs. solver-specific parameters, and what each solver rejects
- **4.3. [MathOpt advanced](../14-mathopt-advanced/README.md)** (Core, module 14, in-progress)
    - 4.3.1 Indicator constraints
    - 4.3.2 Prioritized objectives with `add_auxiliary_objective`
    - 4.3.3 Solution hints and `ModelSolveParameters`
    - 4.3.4 Incremental solving: edit the model, re-solve
    - 4.3.5 Callbacks and `compute_infeasible_subsystem`
- **4.4. [CP-SAT core](../15-cpsat-core/README.md)** (Core, module 15, in-progress)
    - 4.4.1 Integer and Boolean variables, linear constraints over integers
    - 4.4.2 Native logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf`
    - 4.4.3 Objectives, integer scaling and solution callbacks
    - 4.4.4 When CP-SAT beats MIP, and when it doesn't
- **4.5. [CP-SAT scheduling](../16-cpsat-scheduling/README.md)** (Deep, module 16, in-progress)
    - 4.5.1 Interval variables and `NoOverlap`
    - 4.5.2 Cumulative resources: crews and outage windows
    - 4.5.3 Element, table and allowed-assignment constraints
    - 4.5.4 Scheduling vegetation crews across circuits
- **4.6. [CP-SAT tuning and diagnostics](../17-cpsat-tuning-and-diagnostics/README.md)** (Core, module 17, in-progress)
    - 4.6.1 Workers, search strategies and LNS
    - 4.6.2 Hints, assumptions and `SufficientAssumptionsForInfeasibility`
    - 4.6.3 Deterministic time, seeds and reproducible runs
    - 4.6.4 Reading the CP-SAT log
- **4.7. [The linear solver wrapper and special-purpose solvers](../18-linear-solver-wrapper/README.md)** (Core, module 18, in-progress)
    - 4.7.1 Reading pywraplp code
    - 4.7.2 Migrating a pywraplp model to MathOpt
    - 4.7.3 Graph and flow solvers: `SimpleMaxFlow` and `SimpleMinCostFlow`
    - 4.7.4 Special-purpose solvers: `LinearSumAssignment`, `KnapsackSolver` and bin packing
- **4.8. [OR-Tools routing](../52-ortools-routing/README.md)** (Core, module 52, in-progress)
    - 4.8.1 The routing model: index manager, transit callbacks and the TSP
    - 4.8.2 Vehicles, capacities and dimensions (CVRP)
    - 4.8.3 Time windows and service times (VRPTW)
    - 4.8.4 Optional visits with penalties, and pickup and delivery
    - 4.8.5 First-solution strategies, local search and search limits

## 5. Other modeling frameworks and solvers

- **5.1. [Pyomo](../19-pyomo/README.md)** (Core, module 19, in-progress)
    - 5.1.1 Concrete models with indexed Sets, Params, Vars and Constraints
    - 5.1.2 Solving with HiGHS and reading results
    - 5.1.3 Pyomo.GDP: disjunctions, big-M and hull transformations
    - 5.1.4 Piecewise functions and the IIS tools
- **5.2. [PuLP](../20-pulp/README.md)** (Survey, module 20, in-progress)
    - 5.2.1 A PuLP model end to end with CBC
    - 5.2.2 Reading PuLP code you inherit
- **5.3. [gurobipy](../21-gurobipy/README.md)** (Core, module 21, in-progress)
    - 5.3.1 Models, attributes and the matrix API
    - 5.3.2 Duals, reduced costs and sensitivity attributes
    - 5.3.3 `computeIIS`, `feasRelax` and `setObjectiveN`
    - 5.3.4 Licenses: size-limited, academic, and cloud/container (WLS)
- **5.4. [Choosing a solver](../22-choosing-a-solver/README.md)** (Core, module 22, in-progress)
    - 5.4.1 The landscape: Gurobi, CPLEX, Xpress, HiGHS, SCIP, CBC, CP-SAT
    - 5.4.2 Honest benchmarking: instance sets, seeds, time-to-gap, shifted geometric mean
    - 5.4.3 License cost and fit for containers
    - 5.4.4 Writing a solver recommendation

## 6. Formulation craft

- **6.1. [Binary logic](../23-binary-logic/README.md)** (Core, module 23, in-progress)
    - 6.1.1 Binary selection and counting constraints
    - 6.1.2 AND, OR, NOT, XOR and implication as linear constraints
    - 6.1.3 At-least-k, at-most-k, exactly-k
    - 6.1.4 Linearizing binary × binary and binary × bounded continuous
- **6.2. [Big-M and indicators](../24-big-m-and-indicators/README.md)** (Core, module 24, in-progress)
    - 6.2.1 Deriving big-M from bounds
    - 6.2.2 What a loose M does to the LP bound and to numerics
    - 6.2.3 Indicator constraints vs. big-M
    - 6.2.4 Disjunctions: big-M vs. hull
- **6.3. [Knapsack and assignment](../25-knapsack-and-assignment/README.md)** (Core, module 25, in-progress)
    - 6.3.1 0-1 and multi-dimensional knapsack
    - 6.3.2 Multiple knapsack and generalized assignment
    - 6.3.3 Cover inequalities that tighten budget rows
- **6.4. [Multi-period timing](../26-multi-period-timing/README.md)** (Core, module 26, done)
    - 6.4.1 Start-time variables x[i,t] and timing windows
    - 6.4.2 Cash-flow spreading across years
    - 6.4.3 Aggregated vs. cumulative (disaggregated) forms
    - 6.4.4 Carry-over budgets and multi-year caps
- **6.5. [Dependencies and groups](../27-dependencies-and-groups/README.md)** (Core, module 27, in-progress)
    - 6.5.1 Must-do vs. discretionary planning groups
    - 6.5.2 Parent-child bundles and all-or-nothing
    - 6.5.3 Mutually exclusive alternatives (repair vs. replace)
    - 6.5.4 Precedence with lags
    - 6.5.5 Jurisdictional and portfolio minimum/maximum spend
    - 6.5.6 Manual overrides as fixed bounds
- **6.6. [Piecewise-linear functions](../28-piecewise-linear/README.md)** (Deep, module 28, in-progress)
    - 6.6.1 Convex piecewise costs without binaries
    - 6.6.2 The lambda (SOS2-style) formulation built from binaries
    - 6.6.3 Incremental and logarithmic formulations
    - 6.6.4 Lifecycle value curves for asset renewal
- **6.7. [Strong formulations](../29-strong-formulations/README.md)** (Deep, module 29, in-progress)
    - 6.7.1 Comparing formulations by their LP bound
    - 6.7.2 Bound tightening and valid inequalities
    - 6.7.3 Symmetry and how to break it
    - 6.7.4 Case study: reformulating GridCap medium

## 7. The capital planning domain

- **7.1. [Utility capital planning](../30-utility-capital-planning/README.md)** (Prose, module 30, in-progress)
    - 7.1.1 How a utility plans capital: programs, portfolios, rate cases
    - 7.1.2 Transmission, distribution and vegetation investments
    - 7.1.3 The planning cycle: Initial, Pre-Opt, Post-Opt, Budget Lock
    - 7.1.4 What planners, finance and regulators each need from the optimizer
- **7.2. [Financial evaluation](../31-financial-evaluation/README.md)** (Core, module 31, in-progress)
    - 7.2.1 Present value, NPV and discount rates
    - 7.2.2 Escalation; real vs. nominal dollars
    - 7.2.3 Annuities, lifecycle cost, equivalent annual cost
    - 7.2.4 Precomputing NPV coefficients by start year
- **7.3. [Asset risk](../32-asset-risk/README.md)** (Core, module 32, in-progress)
    - 7.3.1 Probability of failure and hazard curves (Weibull)
    - 7.3.2 Remaining useful life: what an ML model actually hands you
    - 7.3.3 Consequence of failure and risk = PoF × CoF
    - 7.3.4 Risk reduction from an intervention, year by year
- **7.4. [Value functions](../33-value-functions/README.md)** (Core, module 33, in-progress)
    - 7.4.1 Benefit measures: reliability, safety, environmental, financial
    - 7.4.2 Normalizing different units
    - 7.4.3 Weights, swing weighting and stakeholder buy-in
    - 7.4.4 Building the CIPT value function

## 8. Multi-objective optimization

- **8.1. [Weighted sums](../34-weighted-sum/README.md)** (Core, module 34, in-progress)
    - 8.1.1 Weighted sums and what the weights really mean
    - 8.1.2 Supported and unsupported Pareto points
- **8.2. [Lexicographic objectives](../35-lexicographic/README.md)** (Core, module 35, in-progress)
    - 8.2.1 Hierarchical objectives with tolerances
    - 8.2.2 Three implementations: auxiliary objectives in MathOpt, `setObjectiveN` in gurobipy, and a manual two-pass solve
- **8.3. [The epsilon-constraint method](../36-epsilon-constraint/README.md)** (Core, module 36, in-progress)
    - 8.3.1 The ε-constraint method
    - 8.3.2 AUGMECON: avoiding weakly efficient points
    - 8.3.3 Generating a frontier and presenting it to planners

## 9. Diagnostics and explainability

- **9.1. [Infeasibility](../37-infeasibility/README.md)** (Core, module 37, in-progress)
    - 9.1.1 Infeasible, unbounded, or the solver can't tell
    - 9.1.2 Validating inputs before the solve
    - 9.1.3 IIS with MathOpt, gurobipy and Pyomo
    - 9.1.4 Elastic constraints and feasibility relaxation
    - 9.1.5 CP-SAT assumptions as a conflict finder
    - 9.1.6 Turning an IIS into a planner message
- **9.2. [Sensitivity for MIP](../38-sensitivity-for-mip/README.md)** (Core, module 38, pending)
    - 9.2.1 Why a MILP has no duals
    - 9.2.2 Fixed-integer LP duals, and when they mean something
    - 9.2.3 Parametric analysis: the budget-value frontier
    - 9.2.4 The marginal value of the next dollar
- **9.3. [Explaining decisions](../39-explaining-decisions/README.md)** (Core, module 39, pending)
    - 9.3.1 A binding-constraints report
    - 9.3.2 Why selected, why deferred: forcing in and out
    - 9.3.3 Scenario diffs: selected, deferred, shifted
    - 9.3.4 Writing results for planners, finance and auditors

## 10. Numerics and determinism

- **10.1. [Numerics](../40-numerics/README.md)** (Deep, module 40, pending)
    - 10.1.1 Floating point, tolerances, and why 1e-6 matters
    - 10.1.2 Coefficient ranges and scaling
    - 10.1.3 Spotting numerical trouble in a log
- **10.2. [Determinism and reproducibility](../41-determinism-and-reproducibility/README.md)** (Core, module 41, in-progress)
    - 10.2.1 Where nondeterminism comes from: threads, time limits, ties
    - 10.2.2 Seeds, threads and deterministic work limits, solver by solver
    - 10.2.3 Alternative optima and deterministic tie-breaking
    - 10.2.4 Versioned input snapshots, pinned solvers and run manifests
    - 10.2.5 Building the deterministic run harness

## 11. Performance at scale

- **11.1. [Model building at scale](../42-model-building-at-scale/README.md)** (Core, module 42, pending)
    - 11.1.1 Measuring build time vs. solve time
    - 11.1.2 Vectorized model building from DataFrames
    - 11.1.3 A generator for 10,000-project portfolios
- **11.2. [Warm starts and tuning](../43-warm-starts-and-tuning/README.md)** (Core, module 43, in-progress)
    - 11.2.1 MIP starts from last cycle's plan
    - 11.2.2 The parameters that matter: presolve, cuts, heuristics, focus
    - 11.2.3 Automated tuning, and how not to overfit it
- **11.3. [Decomposition and heuristics](../44-decomposition-and-heuristics/README.md)** (Deep, module 44, in-progress)
    - 11.3.1 Lagrangian relaxation and subgradient optimization
    - 11.3.2 Benders decomposition
    - 11.3.3 Logic-based Benders
    - 11.3.4 Column generation in one worked example
    - 11.3.5 Rolling horizon and LNS heuristics
- **11.4. [GPU acceleration](../57-gpu-acceleration/README.md)** (Core, module 57, pending)
    - 11.4.1 Why first-order LP methods suit a GPU: PDHG and PDLP
    - 11.4.2 Detecting a GPU, with a CPU fallback that gives the same answer
    - 11.4.3 PDLP on CPU vs. GPU: a measured comparison with HiGHS (cuPDLP-C) and OR-Tools
    - 11.4.4 Determinism on a GPU: what repeats, what doesn't, and what the manifest records
    - 11.4.5 MIP on a GPU: what cuOpt accelerates and why branch-and-bound stays on the CPU
    - 11.4.6 One run policy for threads, workers and the GPU

## 12. Engineering the optimization service

- **12.1. [The scenario workflow](../45-scenario-workflow/README.md)** (Core, module 45, in-progress)
    - 12.1.1 Scenarios as data: create, copy, optimize
    - 12.1.2 Manual overrides as bounds, with an audit trail
    - 12.1.3 Planning-cycle states and locking
    - 12.1.4 Storing scenarios and results in SQLite
- **12.2. [Input data quality](../46-input-data-quality/README.md)** (Core, module 46, in-progress)
    - 12.2.1 Schemas for model inputs
    - 12.2.2 Data-quality checks that prevent infeasibility
    - 12.2.3 Versioned snapshots and content hashes
- **12.3. [Testing optimization code](../47-testing-optimization-code/README.md)** (Core, module 47, in-progress)
    - 12.3.1 Unit-testing one constraint at a time
    - 12.3.2 Property-based tests with Hypothesis
    - 12.3.3 Golden datasets and regression tests
    - 12.3.4 Determinism tests and back-testing against history
- **12.4. [The optimization API](../48-optimization-api/README.md)** (Core, module 48, in-progress)
    - 12.4.1 A REST API with FastAPI
    - 12.4.2 Long solves: submit, poll, fetch
    - 12.4.3 Result schemas planners can consume
- **12.5. [Cloud deployment](../49-cloud-deployment/README.md)** (Core, module 49, pending)
    - 12.5.1 Containerizing a solver service
    - 12.5.2 AWS Batch on Fargate, Step Functions and Lambda: who does what
    - 12.5.3 S3 and a local SQLite file for snapshots and results
    - 12.5.4 Testing AWS code against moto
    - 12.5.5 Terraform for the optimization stack
    - 12.5.6 CI/CD with GitHub Actions

## 13. Capstone

- **13.1. [Capstone: CIPT Lite](../51-capstone-cipt-lite/README.md)** (Core, module 51, pending)
    - 13.1.1 Data: load, validate and snapshot the portfolio
    - 13.1.2 Model: multi-period selection with all section 6 rules
    - 13.1.3 Value: NPV by start year, risk reduction from PoF/RUL, weighted value
    - 13.1.4 Diagnostics: pre-solve checks, IIS message, why-deferred report
    - 13.1.5 Trust: determinism harness, Hypothesis properties, golden test, warm start
    - 13.1.6 Service: FastAPI job API, moto-tested S3 store, Pareto frontier endpoint

## 14. Growing real projects

- **14.1. [Project: vegetation crew planner](../54-project-vegetation-crews/README.md)** (Core, module 54, pending)
    - 14.1.1 The first request: which circuits to trim this year
    - 14.1.2 Crews and months: capacity over time
    - 14.1.3 A trim takes weeks on one crew: from MILP to CP-SAT intervals
    - 14.1.4 Risk grows while a circuit waits: the objective changes
    - 14.1.5 Weather and access windows: calendars and optional work
    - 14.1.6 Planner overrides and why a plan failed
    - 14.1.7 The same plan every run: determinism and regression tests
    - 14.1.8 From script to service, and what the code became
- **14.2. [Project: CIPT planner](../55-project-cipt-planner/README.md)** (Core, module 55, pending)
    - 14.2.1 The first request: fund projects within one budget
    - 14.2.2 Many years: start years, windows and cash-flow spreading
    - 14.2.3 Business rules: must-dos, bundles, parents and alternatives
    - 14.2.4 Value: NPV by start year and risk reduction
    - 14.2.5 Two goals: risk against NPV
    - 14.2.6 Why it failed, why it was deferred: a diagnostics layer
    - 14.2.7 Scenarios, overrides and snapshots
    - 14.2.8 Trust at scale: determinism harness, golden tests, warm starts
- **14.3. [Project: transformer fleet renewal](../56-project-transformer-renewal/README.md)** (Core, module 56, pending)
    - 14.3.1 The first request: replace the worst transformers, and why ranking is not enough
    - 14.3.2 A ten-year budget and Weibull failure risk
    - 14.3.3 Substation bundles and outage coordination
    - 14.3.4 Crews, lead times and spare units
    - 14.3.5 From 500 to 5,000 transformers: building the model at scale
    - 14.3.6 Too slow: a stronger formulation and a rolling horizon
    - 14.3.7 Uncertain failure curves: scenarios and what changes
    - 14.3.8 Handoff: tests, packaging and a report for finance
- **14.4. [Project: spec-driven development with OpenSpec](../58-project-sdd-openspec/README.md)** (Core, module 58, pending)
    - 14.4.1 Baseline specs: write down what the planner already does
    - 14.4.2 A regional spend share: the first change from proposal to archive
    - 14.4.3 A must-do override that needs a recorded reason
    - 14.4.4 Carry-over: a MODIFIED budget rule and a RENAMED requirement
    - 14.4.5 Retiring the yearly start cap: a REMOVED requirement
    - 14.4.6 Living specs: every scenario traced to a test, every test to a scenario

## 15. Mock interviews

- **15.1. [Mock interviews](../53-mock-interviews/README.md)** (Core, module 53, pending)
    - 15.1.1 Mock 1: modeling and formulation
    - 15.1.2 Mock 2: solvers, OR-Tools and the search
    - 15.1.3 Mock 3: value, objectives and trade-offs
    - 15.1.4 Mock 4: diagnostics, sensitivity and explanations
    - 15.1.5 Mock 5: production, trust and performance
    - 15.1.6 Mixed mock A: a technical screen
    - 15.1.7 Mixed mock B: an onsite loop
