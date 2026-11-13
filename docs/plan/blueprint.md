# Integer Programming with Python and Google OR-Tools: Course Blueprint

This is the table of contents and build brief for a from-scratch course that teaches what an optimization engineer needs to build a capital investment planning tool (CIPT). It goes from what an optimization model is to a tested, deployed capital-planning MILP service. It is written for a Claude Code agent that will author the course in a repository and publish it with [StudyForge](https://github.com/msorkhpar/studyforge), following the layout of [Claude-senior-java-engineer](https://github.com/msorkhpar/Claude-senior-java-engineer).

The agent should also read the resource list in [resource-links.md](resource-links.md).

## At a glance

The course has 15 sections, 57 modules and 237 lessons, for about 76 learner hours (60 hours of modules plus a 5-hour capstone, at about 20 minutes per lesson), plus an optional "Going deeper" part at the end of each section. Every lesson has runnable Python examples, a quiz, and two or three code practices (Core and Deep lessons; a Survey lesson may have none).

|  |  |
| --- | --- |
| Audience | A software engineer who writes basic Python and has never built an optimization model |
| Prerequisites | Python functions, loops, dicts and classes; high-school algebra. Everything else is taught, including the linear algebra the course needs. |
| Main stack | Google OR-Tools: MathOpt for MILP and LP, CP-SAT for logic and scheduling. HiGHS is the default open-source backend. |
| Also taught | Pyomo, PuLP, gurobipy (size-limited license), SCIP via MathOpt; pandas, pytest, Hypothesis, FastAPI, boto3 with moto |
| Running project | GridCap, a fictional utility's capital portfolio, extended in every section and finished in the capstone |
| End state | The learner can build, diagnose, explain, test and package a CIPT-style multi-period capital-planning MILP |

**Depth tags used below**

- **Core:** needed for the work the course prepares for. Full lessons, examples, practices and a quiz.
- **Deep:** goes under the hood, such as writing your own branch-and-bound or a Benders loop. The core path walks through a guided version where most of the code is given. Building it from scratch is an optional Stretch practice.
- **Survey:** orientation only. Short lessons and a quiz, few or no practices.
- **Prose:** the topic can't run in the offline runner (Docker, Terraform, CI). Lessons and quizzes only.

**Learning path.** Sections 1–3 are strictly in order. Section 4 (OR-Tools) needs section 2. Section 5 can be taken any time after section 4. Sections 6–7 need sections 3 and 4. Sections 8–11 need section 6. Section 12 needs sections 9 and 10. The capstone needs everything.

## Course-wide conventions

These rules apply to every section. Adapting the material to StudyForge (repository layout, toolchain, runner) is covered by the authoring documents in `docs/`.

- **Numbering.** Lessons are numbered section.module.lesson, for example 6.4.2. Modules are numbered 01–58 across the whole course (50 is unused: its section was dropped) and get slugs like `26-multi-period-timing`. This is the same hierarchy as the Java course.
- **Every lesson** opens with one concrete GridCap problem and teaches through small runnable examples with their real output. It ends with a quiz. Practices sit right after the section they test. Time budget: a lesson takes about 20 minutes, has 2–4 runnable examples and a 3-question quiz, and its two or three practices fit in about 20 minutes together (5–10 minutes each). Longer builds, such as a full branch-and-bound or a Benders loop from scratch, are tagged as Stretch practices, are optional, and don't count toward the module's time.
- **"Going deeper" at the end of each section.** This comes after the section's practices and is for learners who need more:
  - **Another angle:** a second explanation of the section's 2–3 hardest ideas, using a different example from the lesson's.
  - **Extra readings:** specific chapters or pages from the resource library, each with one line on what it adds.
  - **Stretch practices:** the optional longer builds.
  - **Budget:** none of this counts toward the 65 hours. It has no time limit and is never required by later sections.
- **Practice types.**
  - **Code practice:** implement a function, graded by tests.
  - **Modeling practice:** turn a business rule written in words into constraints. The tests check feasibility and infeasibility on hand-made plans, so any correct formulation passes.
  - **Quiz:** 3–5 questions per lesson, each answer explained.
- **GridCap, the running dataset.** A fictional utility's capital portfolio, generated from a seed.
  - **Projects:** program (transmission, distribution or vegetation), region, cost profile by year, earliest and latest start, must-do flag, parent, alternative group, NPV by start year.
  - **Assets:** PoF curve, RUL, consequence of failure.
  - **Limits:** budgets by year and region, and crews.
  - **Sizes:** tiny (8 projects, checkable by hand), small (40), medium (400) and large (10,000, for performance work).
  - **Rule:** never present it as a real utility's data.
- **Read-along topics.** Docker, Terraform and CI are taught with read-along code and quizzes. AWS code is tested against moto mocks.
- **API facts to respect** (verified on OR-Tools 9.15):
  - MathOpt has `compute_infeasible_subsystem` and `add_auxiliary_objective`.
  - Neither the Python MathOpt API nor CP-SAT has SOS constraints.
  - HiGHS rejects `threads` through MathOpt.
  - MathOpt hints go in `ModelSolveParameters(solution_hints=...)`.

## Sections 1–3: Foundations, linear programming, integer programming

### Section 1. Foundations

GridCap milestone: load the tiny portfolio, check that a hand-made plan is valid, and find the best plan by brute force.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 01-optimization-mindset | 1.1.1 Decisions, objectives and constraints: turning a planner's question into a model · 1.1.2 Predictive vs. prescriptive: where PoF/RUL predictions stop and optimization starts · 1.1.3 The problem zoo: LP, MILP, CP, NLP and how to pick | Evaluate a plan's cost and value in plain Python; brute-force the best of 2^8 plans; the five parts of a MathOpt program and its status. Practice: `evaluate_plan`, `brute_force_best` | Core · 65 min |
| 02-math-toolkit | 1.2.1 Vectors, matrices and Ax ≤ b in NumPy · 1.2.2 Sparse model matrices and why solvers rely on sparsity · 1.2.3 Convex sets, polyhedra and extreme points | Build GridCap's budget matrix; vectorized feasibility check. Practice: `is_feasible(A, b, x)`, build a CSR matrix | Core · 65 min |
| 03-python-for-optimization | 1.3.1 Preparing model input with pandas · 1.3.2 Typed inputs with dataclasses and pydantic · 1.3.3 Testing numerical code with pytest: tolerances, fixtures, parametrize | Load and validate GridCap CSVs, rejecting bad rows. Practice: validator with 6 failing-row cases | Core · 65 min |

### Section 2. Linear programming

GridCap milestone: an LP that allocates budget across programs, with carry-over between years, and the dual values of its budget constraints.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 04-lp-modeling | 2.1.1 Your first LP: splitting a maintenance budget across programs · 2.1.2 Standard form, slack and surplus · 2.1.3 LP patterns: blending, flows, multi-period carry-over | Solve with MathOpt and GLOP. Practice: carry-over budget LP | Core · 85 min |
| 05-lp-geometry-and-simplex | 2.2.1 Solving a 2-variable LP by picture · 2.2.2 Simplex as walking between vertices (a tiny tableau implementation) · 2.2.3 Infeasible, unbounded and degenerate LPs | matplotlib feasible region; a 60-line simplex. Practice: one pivot step; detect unboundedness | Deep · 65 min |
| 06-duality-and-sensitivity | 2.3.1 The dual LP and what its variables price · 2.3.2 Weak and strong duality, complementary slackness · 2.3.3 Shadow prices, reduced costs and ranging from a solver · 2.3.4 Explaining a dual value to a finance partner | Read MathOpt `dual_values` and `reduced_costs`. Practice: check complementary slackness numerically | Core · 85 min |
| 07-lp-solvers-in-practice | 2.4.1 Simplex, interior point and PDLP: GLOP, HiGHS, PDLP · 2.4.2 Reading an LP solver log · 2.4.3 Re-solving after the data changes | Practice: same model on 3 solvers, with objectives equal within tolerance | Survey · 40 min |

### Section 3. Integer programming foundations

GridCap milestone: a 0-1 project-selection knapsack, solved by your own branch-and-bound and checked against HiGHS.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 08-why-integers | 3.1.1 Yes/no decisions, and why rounding an LP fails · 3.1.2 The integrality gap, measured on GridCap · 3.1.3 Why MILP is hard: combinatorial growth in numbers | Show rounding breaking the budget. Practice: compute the LP bound and the integrality gap | Core · 65 min |
| 09-branch-and-bound | 3.2.1 Branching on a fractional variable · 3.2.2 Bounds, incumbents and pruning · 3.2.3 Node and variable selection · 3.2.4 A knapsack branch-and-bound in 116 lines | Practice: B&B with a fractional-knapsack bound, graded against brute force on 20 seeds | Deep · 105 min |
| 10-cuts-presolve-heuristics | 3.3.1 Cutting planes: Gomory and cover cuts by hand · 3.3.2 Presolve: what the solver removes first · 3.3.3 Primal heuristics: rounding, diving, RINS · 3.3.4 Reading a full MIP log line by line | Practice: find a violated cover inequality for a budget row; quiz on an annotated log | Deep · 85 min |
| 11-mip-gap-and-termination | 3.4.1 Best bound, incumbent, absolute and relative gap · 3.4.2 Stopping on gap, time, nodes or solution count · 3.4.3 What "optimal at 0.01%" means on a $2B portfolio | Practice: gap from `SolveResult`; pick limits for a scenario | Core · 40 min |

## Sections 4–5: OR-Tools in depth, other frameworks and solvers

### Section 4. Google OR-Tools in depth

GridCap milestone: the same selection model written once in MathOpt and solved with HiGHS, SCIP and CP-SAT, plus a CP-SAT crew schedule for vegetation work, crew-to-site assignment and spares flows with OR-Tools' special-purpose solvers, and inspection-crew routes with the routing library.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 12-ortools-landscape | 4.1.1 What's in OR-Tools: MathOpt, CP-SAT, linear solver wrapper, routing, graph · 4.1.2 Versions and the backends that ship with it · 4.1.3 Choosing an API for a problem | Quiz-heavy: which API for 10 problem statements | Survey · 20 min |
| 13-mathopt-core | 4.2.1 Model, variables, constraints, objective · 4.2.2 Reading `SolveResult`: termination, primal and dual solutions, statistics · 4.2.3 Switching solvers: HiGHS, SCIP, CP-SAT, GLOP, Gurobi · 4.2.4 Common vs. solver-specific parameters, and what each solver rejects | Practice: a solver-agnostic `solve_selection(df, budget, solver)`; a termination-reason handler | Core · 85 min |
| 14-mathopt-advanced | 4.3.1 Indicator constraints · 4.3.2 Prioritized objectives with `add_auxiliary_objective` · 4.3.3 Solution hints and `ModelSolveParameters` · 4.3.4 Incremental solving: edit the model, re-solve · 4.3.5 Callbacks and `compute_infeasible_subsystem` | Practice: re-solve a scenario after a budget cut without rebuilding the model; read an IIS | Core · 105 min |
| 15-cpsat-core | 4.4.1 Integer and Boolean variables, linear constraints over integers · 4.4.2 Native logic: `AddBoolOr`, `AddImplication`, `OnlyEnforceIf` · 4.4.3 Objectives, integer scaling and solution callbacks · 4.4.4 When CP-SAT beats MIP, and when it doesn't | Practice: the GridCap bundle rules in CP-SAT with no big-M; enumerate all optimal plans with a callback | Core · 85 min |
| 16-cpsat-scheduling | 4.5.1 Interval variables and `NoOverlap` · 4.5.2 Cumulative resources: crews and outage windows · 4.5.3 Element, table and allowed-assignment constraints · 4.5.4 Scheduling vegetation crews across circuits | Practice: crew schedule that minimizes risk-weighted lateness | Deep · 105 min |
| 17-cpsat-tuning-and-diagnostics | 4.6.1 Workers, search strategies and LNS · 4.6.2 Hints, assumptions and `SufficientAssumptionsForInfeasibility` · 4.6.3 Deterministic time, seeds and reproducible runs · 4.6.4 Reading the CP-SAT log | Practice: find which rule flags make a scenario infeasible | Core · 65 min |
| 18-linear-solver-wrapper | 4.7.1 Reading pywraplp code · 4.7.2 Migrating a pywraplp model to MathOpt · 4.7.3 Graph and flow solvers: `SimpleMaxFlow` and `SimpleMinCostFlow` · 4.7.4 Special-purpose solvers: `LinearSumAssignment`, `KnapsackSolver` and bin packing | Practice: port a given pywraplp model, with tests proving the same answer; crew-to-site assignment with `LinearSumAssignment` checked against the MIP; spares shipped as a min-cost flow | Core · 65 min |
| 52-ortools-routing | 4.8.1 The routing model: index manager, transit callbacks and the TSP · 4.8.2 Vehicles, capacities and dimensions (CVRP) · 4.8.3 Time windows and service times (VRPTW) · 4.8.4 Optional visits with penalties, and pickup and delivery · 4.8.5 First-solution strategies, local search and search limits | Examples adapted from the OR-Tools routing guides; practice: inspection-crew routes to GridCap substations with time windows, crew capacity and droppable low-priority visits | Core · 105 min |

### Section 5. Other modeling frameworks and solvers

GridCap milestone: the same model in Pyomo and gurobipy, plus a benchmark report that recommends a solver.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 19-pyomo | 5.1.1 Concrete models with indexed Sets, Params, Vars and Constraints · 5.1.2 Solving with HiGHS and reading results · 5.1.3 Pyomo.GDP: disjunctions, big-M and hull transformations · 5.1.4 Piecewise functions and the IIS tools | Practice: GDP model for repair-vs-replace; compare big-M and hull LP bounds | Core · 85 min |
| 20-pulp | 5.2.1 A PuLP model end to end with CBC · 5.2.2 Reading PuLP code you inherit | Practice: fix a buggy PuLP model | Survey · 20 min |
| 21-gurobipy | 5.3.1 Models, attributes and the matrix API · 5.3.2 Duals, reduced costs and sensitivity attributes · 5.3.3 `computeIIS`, `feasRelax` and `setObjectiveN` · 5.3.4 Licenses: size-limited, academic, and cloud/container (WLS) | Practice: an IIS report and the feasibility relaxation of an infeasible scenario | Core · 85 min |
| 22-choosing-a-solver | 5.4.1 The landscape: Gurobi, CPLEX, Xpress, HiGHS, SCIP, CBC, CP-SAT · 5.4.2 Honest benchmarking: instance sets, seeds, time-to-gap, shifted geometric mean · 5.4.3 License cost and fit for containers · 5.4.4 Writing a solver recommendation | Practice: a benchmark harness that reports the shifted geometric mean over seeds | Core · 65 min |

## Sections 6–7: Formulation craft, capital planning domain

### Section 6. Formulation craft

This is the heart of the course. GridCap milestone: the full multi-period model with every CIPT business rule, a lifecycle value curve, and a reformulation that solves faster.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 23-binary-logic | 6.1.1 Binary selection and counting constraints · 6.1.2 AND, OR, NOT, XOR and implication as linear constraints · 6.1.3 At-least-k, at-most-k, exactly-k · 6.1.4 Linearizing binary × binary and binary × bounded continuous | Modeling practices: 8 rules written in words, each checked on feasible and infeasible plans | Core · 85 min |
| 24-big-m-and-indicators | 6.2.1 Deriving big-M from bounds · 6.2.2 What a loose M does to the LP bound and to numerics · 6.2.3 Indicator constraints vs. big-M · 6.2.4 Disjunctions: big-M vs. hull | Practice: compute the tightest valid M from data; measure the bound with M = 1e6 vs. the tight M | Core · 65 min |
| 25-knapsack-and-assignment | 6.3.1 0-1 and multi-dimensional knapsack · 6.3.2 Multiple knapsack and generalized assignment · 6.3.3 Cover inequalities that tighten budget rows | Practice: assign projects to crews and years (GAP) | Core · 65 min |
| 26-multi-period-timing | 6.4.1 Start-time variables x\[i,t\] and timing windows · 6.4.2 Cash-flow spreading across years · 6.4.3 Aggregated vs. cumulative (disaggregated) forms · 6.4.4 Carry-over budgets and multi-year caps | Practice: build `spend_by_year` expressions; prove the cumulative form gives a tighter bound | Core · 105 min |
| 27-dependencies-and-groups | 6.5.1 Must-do vs. discretionary planning groups · 6.5.2 Parent-child bundles and all-or-nothing · 6.5.3 Mutually exclusive alternatives (repair vs. replace) · 6.5.4 Precedence with lags · 6.5.5 Jurisdictional and portfolio minimum/maximum spend · 6.5.6 Manual overrides as fixed bounds | Modeling practices: one per rule, all on GridCap small | Core · 125 min |
| 28-piecewise-linear | 6.6.1 Convex piecewise costs without binaries · 6.6.2 The lambda (SOS2-style) formulation built from binaries · 6.6.3 Incremental and logarithmic formulations · 6.6.4 Lifecycle value curves for asset renewal | Practice: a value curve with 5 breakpoints in MathOpt; check against a Pyomo Piecewise version | Deep · 65 min |
| 29-strong-formulations | 6.7.1 Comparing formulations by their LP bound · 6.7.2 Bound tightening and valid inequalities · 6.7.3 Symmetry and how to break it · 6.7.4 Case study: reformulating GridCap medium | Practice: add symmetry breaking for identical assets and measure the node count | Deep · 65 min |

### Section 7. The capital planning domain

GridCap milestone: coefficients the model can trust: NPV by start year, risk reduction from PoF and RUL, and a normalized multi-attribute value per project.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 30-utility-capital-planning | 7.1.1 How a utility plans capital: programs, portfolios, rate cases · 7.1.2 Transmission, distribution and vegetation investments · 7.1.3 The planning cycle: Initial, Pre-Opt, Post-Opt, Budget Lock · 7.1.4 What planners, finance and regulators each need from the optimizer | Quizzes; a stakeholder-requirements worksheet | Prose · 40 min |
| 31-financial-evaluation | 7.2.1 Present value, NPV and discount rates · 7.2.2 Escalation; real vs. nominal dollars · 7.2.3 Annuities, lifecycle cost, equivalent annual cost · 7.2.4 Precomputing NPV coefficients by start year | Practice: an `npv_by_start_year` table, checked against numpy-financial | Core · 65 min |
| 32-asset-risk | 7.3.1 Probability of failure and hazard curves (Weibull) · 7.3.2 Remaining useful life: what an ML model actually hands you · 7.3.3 Consequence of failure and risk = PoF × CoF · 7.3.4 Risk reduction from an intervention, year by year | Practice: risk-reduction coefficients from Weibull parameters, checked with scipy.stats | Core · 85 min |
| 33-value-functions | 7.4.1 Benefit measures: reliability, safety, environmental, financial · 7.4.2 Normalizing different units · 7.4.3 Weights, swing weighting and stakeholder buy-in · 7.4.4 Building the CIPT value function | Practice: a normalized value function; test that its rankings don't change under rescaling | Core · 65 min |

## Sections 8–10: Multi-objective, diagnostics and explainability, numerics and determinism

### Section 8. Multi-objective optimization

GridCap milestone: an NPV vs. risk-reduction Pareto frontier for planners, and a lexicographic plan with a 1% NPV tolerance.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 34-weighted-sum | 8.1.1 Weighted sums and what the weights really mean · 8.1.2 Supported and unsupported Pareto points | Practice: find a Pareto point no choice of weights can reach | Core · 40 min |
| 35-lexicographic | 8.2.1 Hierarchical objectives with tolerances · 8.2.2 Three implementations: auxiliary objectives in MathOpt, `setObjectiveN` in gurobipy, and a manual two-pass solve | Practice: a manual two-pass solve that matches the solver-native version | Core · 40 min |
| 36-epsilon-constraint | 8.3.1 The ε-constraint method · 8.3.2 AUGMECON: avoiding weakly efficient points · 8.3.3 Generating a frontier and presenting it to planners | Practice: frontier generator; tests that every point is non-dominated | Core · 65 min |

### Section 9. Diagnostics and explainability

GridCap milestone: an infeasible Budget Lock scenario explained in one planner-readable message, plus a "why deferred" report for every unfunded project.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 37-infeasibility | 9.1.1 Infeasible, unbounded, or the solver can't tell · 9.1.2 Validating inputs before the solve · 9.1.3 IIS with MathOpt, gurobipy and Pyomo · 9.1.4 Elastic constraints and feasibility relaxation · 9.1.5 CP-SAT assumptions as a conflict finder · 9.1.6 Turning an IIS into a planner message | Practices: pre-solve checks that catch 5 known infeasibility causes; an IIS-to-message translator | Core · 125 min |
| 38-sensitivity-for-mip | 9.2.1 Why a MILP has no duals · 9.2.2 Fixed-integer LP duals, and when they mean something · 9.2.3 Parametric analysis: the budget-value frontier · 9.2.4 The marginal value of the next dollar | Practice: a budget-value curve built by repeated solves; its step points | Core · 85 min |
| 39-explaining-decisions | 9.3.1 A binding-constraints report · 9.3.2 Why selected, why deferred: forcing in and out · 9.3.3 Scenario diffs: selected, deferred, shifted · 9.3.4 Writing results for planners, finance and auditors | Practice: a `diff_scenarios(a, b)` that reports adds, drops and timing shifts | Core · 85 min |

### Section 10. Numerics and determinism

GridCap milestone: a run harness that gives byte-identical result manifests across 10 runs, and a scaled model that no longer warns about its numerics.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 40-numerics | 10.1.1 Floating point, tolerances, and why 1e-6 matters · 10.1.2 Coefficient ranges and scaling · 10.1.3 Spotting numerical trouble in a log | Practice: rescale a badly scaled model and assert its coefficient range shrinks | Deep · 40 min |
| 41-determinism-and-reproducibility | 10.2.1 Where nondeterminism comes from: threads, time limits, ties · 10.2.2 Seeds, threads and deterministic work limits, solver by solver · 10.2.3 Alternative optima and deterministic tie-breaking · 10.2.4 Versioned input snapshots, pinned solvers and run manifests · 10.2.5 Building the deterministic run harness | Practice: a harness whose determinism test passes on HiGHS and CP-SAT | Core · 85 min |

## Sections 11–12: Performance, engineering the service

### Section 11. Performance at scale

GridCap milestone: the large portfolio (10,000 projects × 10 years) built in seconds, warm-started from last cycle's plan, and solved within a target time by decomposition.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 42-model-building-at-scale | 11.1.1 Measuring build time vs. solve time · 11.1.2 Vectorized model building from DataFrames · 11.1.3 A generator for 10,000-project portfolios | Practice: speed up a slow builder 10×, with a test that the models are identical | Core · 65 min |
| 43-warm-starts-and-tuning | 11.2.1 MIP starts from last cycle's plan · 11.2.2 The parameters that matter: presolve, cuts, heuristics, focus · 11.2.3 Automated tuning, and how not to overfit it | Practice: hint from a greedy plan; measure time to first incumbent | Core · 65 min |
| 44-decomposition-and-heuristics | 11.3.1 Lagrangian relaxation and subgradient optimization · 11.3.2 Benders decomposition · 11.3.3 Logic-based Benders · 11.3.4 Column generation in one worked example · 11.3.5 Rolling horizon and LNS heuristics | Practices: Lagrangian bound on the multi-year budget; a Benders loop checked against the monolithic solve | Deep · 125 min |
| 57-gpu-acceleration | 11.4.1 Why first-order LP methods suit a GPU: PDHG and PDLP · 11.4.2 Detecting a GPU, with a CPU fallback that gives the same answer · 11.4.3 PDLP on CPU vs. GPU: a measured comparison with HiGHS (cuPDLP-C) and OR-Tools · 11.4.4 Determinism on a GPU: what repeats, what doesn't, and what the manifest records · 11.4.5 MIP on a GPU: what cuOpt accelerates and why branch-and-bound stays on the CPU · 11.4.6 One run policy for threads, workers and the GPU | Practices run on the CPU everywhere and add GPU checks when a GPU is found; a repeatability test across devices within tolerance | Core · 90 min |

### Section 12. Engineering the optimization service

GridCap milestone: a scenario service you can call over REST. It stores versioned inputs and results, runs long solves as jobs, has a full test suite, and is packaged for AWS.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 45-scenario-workflow | 12.1.1 Scenarios as data: create, copy, optimize · 12.1.2 Manual overrides as bounds, with an audit trail · 12.1.3 Planning-cycle states and locking · 12.1.4 Storing scenarios and results in SQLite | Practice: copy a scenario, override 3 projects, re-optimize, and diff the results | Core · 85 min |
| 46-input-data-quality | 12.2.1 Schemas for model inputs · 12.2.2 Data-quality checks that prevent infeasibility · 12.2.3 Versioned snapshots and content hashes | Practice: reject a snapshot with 6 planted defects | Core · 40 min |
| 47-testing-optimization-code | 12.3.1 Unit-testing one constraint at a time · 12.3.2 Property-based tests with Hypothesis · 12.3.3 Golden datasets and regression tests · 12.3.4 Determinism tests and back-testing against history | Practice: Hypothesis properties (spend within budget, must-dos always funded, children never without parents) | Core · 85 min |
| 48-optimization-api | 12.4.1 A REST API with FastAPI · 12.4.2 Long solves: submit, poll, fetch · 12.4.3 Result schemas planners can consume | Practice: a job endpoint tested with FastAPI's TestClient | Core · 65 min |
| 49-cloud-deployment | 12.5.1 Containerizing a solver service · 12.5.2 AWS Batch on Fargate, Step Functions and Lambda: who does what · 12.5.3 S3 and a local SQLite file for snapshots and results · 12.5.4 Testing AWS code against moto · 12.5.5 Terraform for the optimization stack · 12.5.6 CI/CD with GitHub Actions | Practices: moto-tested S3 snapshot store and Batch job submitter. 12.5.1, 12.5.5 and 12.5.6 are read-along | Core · 105 min |

## Section 13: Capstone and real-world practice projects

### Module 51-capstone-cipt-lite (about 5 hours)

The learner builds a small, complete CIPT on the GridCap medium portfolio. Each milestone is a lesson with a graded practice that builds on the one before, and the milestones run in this order. It fits in 5 hours because each milestone assembles code the learner already wrote in earlier modules.

| Lesson | Milestone | Graded by |
| --- | --- | --- |
| 13.1.1 | Data: load, validate and snapshot the portfolio | Defect-planted snapshots rejected; content hash stable |
| 13.1.2 | Model: multi-period selection with all section 6 rules | Feasibility tests on hand-built plans; objective equals the reference within tolerance |
| 13.1.3 | Value: NPV by start year, risk reduction from PoF/RUL, weighted value | Coefficient tables match the reference |
| 13.1.4 | Diagnostics: pre-solve checks, IIS message, why-deferred report | An infeasible Budget Lock scenario yields the expected message |
| 13.1.5 | Trust: determinism harness, Hypothesis properties, golden test, warm start | 10 identical manifests; properties hold on 200 generated portfolios |
| 13.1.6 | Service: FastAPI job API, moto-tested S3 store, Pareto frontier endpoint | API tests pass offline |

### Section 14. Growing real projects

Four projects, each grown from a first small request into a multi-file codebase, one new requirement per lesson. Each lesson:
- opens with the requirement as a planner or engineer would write it;
- says what the current code can't do and why;
- shows the design decision and its alternatives;
- shows the change file by file (each class, method, variable or row before and after, with the reason for each change) and the formulation before and after;
- adds the tests the requirement needs, shows the output before and after, and says what the step did to the code's size, complexity and style.

The learner navigates the whole project at every step: the step's practice is a project practice whose starter is the code before the change, graded by the tests that the change adds. The projects draw on the whole course in different shapes:
- the vegetation crew planner grows from a knapsack into CP-SAT scheduling;
- the CIPT planner grows into a full multi-year capital investment planner;
- the transformer fleet renewal grows into a model that needs scale and decomposition;
- the spec-driven capital planner grows one OpenSpec change at a time: each request becomes a proposal, a spec delta with requirements and scenarios, and tasks, its scenarios become tests that fail before the code changes, and the change is archived into living specs that every test traces to.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 54-project-vegetation-crews | 14.1.1 The first request: which circuits to trim this year · 14.1.2 Crews and months: capacity over time · 14.1.3 A trim takes weeks on one crew: from MILP to CP-SAT intervals · 14.1.4 Risk grows while a circuit waits: the objective changes · 14.1.5 Weather and access windows: calendars and optional work · 14.1.6 Planner overrides and why a plan failed · 14.1.7 The same plan every run: determinism and regression tests · 14.1.8 From script to service, and what the code became | Each step: the before and after of every changed file, its tests, and a project practice that implements the step from the before code | Core · 160 min |
| 55-project-cipt-planner | 14.2.1 The first request: fund projects within one budget · 14.2.2 Many years: start years, windows and cash-flow spreading · 14.2.3 Business rules: must-dos, bundles, parents and alternatives · 14.2.4 Value: NPV by start year and risk reduction · 14.2.5 Two goals: risk against NPV · 14.2.6 Why it failed, why it was deferred: a diagnostics layer · 14.2.7 Scenarios, overrides and snapshots · 14.2.8 Trust at scale: determinism harness, golden tests, warm starts | Each step: the before and after of every changed file, its tests, and a project practice that implements the step from the before code | Core · 160 min |
| 56-project-transformer-renewal | 14.3.1 The first request: replace the worst transformers, and why ranking is not enough · 14.3.2 A ten-year budget and Weibull failure risk · 14.3.3 Substation bundles and outage coordination · 14.3.4 Crews, lead times and spare units · 14.3.5 From 500 to 5,000 transformers: building the model at scale · 14.3.6 Too slow: a stronger formulation and a rolling horizon · 14.3.7 Uncertain failure curves: scenarios and what changes · 14.3.8 Handoff: tests, packaging and a report for finance | Each step: the before and after of every changed file, its tests, and a project practice that implements the step from the before code | Core · 160 min |
| 58-project-sdd-openspec | 14.4.1 Baseline specs: write down what the planner already does · 14.4.2 A regional spend share: the first change from proposal to archive · 14.4.3 A must-do override that needs a recorded reason · 14.4.4 Carry-over: a MODIFIED budget rule and a RENAMED requirement · 14.4.5 Retiring the yearly start cap: a REMOVED requirement · 14.4.6 Living specs: every scenario traced to a test, every test to a scenario | Each step: one OpenSpec change (proposal, spec delta, tasks, archive), tests written from its scenarios that fail before the code changes, the before and after of every changed file, and a project practice that implements the step from the before code; a Python checker mirrors `openspec validate --strict` in the runner | Core · 120 min |

### Section 15. Mock interviews

The last module, after the grown projects of section 14: interview rounds built from the whole course, the three projects included. Five mocks each take one area of the role; the last two mix every area the way a real loop does. Each question has a model answer the learner opens after answering, the follow-ups an interviewer asks next, and a pointer to the lesson that teaches it. Each mock includes trap questions built from common wrong answers, and one whiteboard formulation that the learner codes and a test grades.

| Module | Lessons | Examples and practices | Depth · time |
| --- | --- | --- | --- |
| 53-mock-interviews | 15.1.1 Mock 1: modeling and formulation · 15.1.2 Mock 2: solvers, OR-Tools and the search · 15.1.3 Mock 3: value, objectives and trade-offs · 15.1.4 Mock 4: diagnostics, sensitivity and explanations · 15.1.5 Mock 5: production, trust and performance · 15.1.6 Mixed mock A: a technical screen · 15.1.7 Mixed mock B: an onsite loop | Each mock: questions with hidden model answers and follow-ups, trap questions, and a whiteboard formulation coded and graded by tests; quizzes drawn from the questions | Core · 160 min |

### Real-world practice projects

The vegetation crew planner and transformer fleet renewal, first planned here, are now walked through step by step in section 14. These are optional standalone projects for after the relevant sections, at 2–4 hours each and outside the 65-hour budget. They form a separate Projects track after the main course. Each one is a full project practice rather than a single function: a small codebase the learner completes across several files. Each project ships with:

- A file explorer over a skeleton package of several modules (data loading, model building, solving, reporting). Signatures are in place and bodies are left to write.
- A method-by-method blueprint: for every method to write, its contract (inputs, outputs, invariants), the modeling idea it needs, and a pointer to the lesson that taught it. This gives enough guidance to finish without giving away the code.
- A full test suite: unit tests per method, end-to-end tests, and an expected-output check that compares the final report against a reference within tolerance.
- Room to work: no limit on how many lines or files the learner changes. Only the tests and the output check decide the grade.
- A dataset generator and a reference solution.

| Project | The question it answers | Draws on sections |
| --- | --- | --- |
| Storm-hardening portfolio | Which undergrounding and pole-replacement projects best cut outage minutes, as a frontier against cost? | 6, 8 |
| Repair vs. replace | For each aging substation, repair now, replace now, or replace later? | 6.5, 5 (GDP), 9 |
| Regulator scenario pack | Rerun the plan under 3 rate-case budget outcomes and explain every difference | 9, 12 |
| EV charger siting | Where should 40 chargers go to maximize coverage under a grid-capacity limit? (Facility location, a transfer exercise outside capital planning) | 6, 11 |

## Resource library

These are the sources the course author should read before writing each section and cite in each lesson's further-reading line. **The OR-Tools documentation and its samples are the primary source** for every OR-Tools topic, in every section: lessons teach the API the way those pages do, adapt their examples (Apache-2.0 code, with a line saying where each came from) and cite them first. The resource list (resource-links.md) has 56 more, grouped by topic.

| Sections | Resource | Use it for |
| --- | --- | --- |
| 1–3, 6 | [Hands-On Mathematical Optimization with Python](https://mobook.github.io/MO-book/) (Postek, Zocca, Gromicho, Kantor; Cambridge UP) | Gentle modeling-first chapters on LP, MILP and networks, with free notebooks (Pyomo) |
| 2 | [Vanderbei, Linear Programming: Foundations and Extensions](https://vanderbei.princeton.edu/LPbook/) | Simplex, duality, sensitivity |
| 3, 6 | [Integer Programming, Chapter 9 of Applied Mathematical Programming (MIT 15.053)](https://web.mit.edu/15.053/www/AMP-Chapter-09.pdf) | Capital budgeting examples, logical constraints, branch-and-bound |
| 3, 6, 29 | [Vielma, MILP Formulation Techniques](https://juan-pablo-vielma.github.io/publications/Mixed-Integer-Linear-Programming-Formulation-Techniques.pdf) | Formulation strength, disjunctions, piecewise-linear models |
| 3, 6 | Williams, *Model Building in Mathematical Programming* (Wiley); Wolsey, *Integer Programming* (Wiley) | The standard references for modeling and theory |
| 4 | [OR-Tools docs](https://developers.google.com/optimization) · [MathOpt](https://developers.google.com/optimization/math_opt) · [CP-SAT](https://developers.google.com/optimization/cp/cp_solver) · [OR-Tools on GitHub](https://github.com/google/or-tools) · [Routing](https://developers.google.com/optimization/routing) · [Network flows](https://developers.google.com/optimization/flow) · [Assignment](https://developers.google.com/optimization/assignment) · [Bin packing and knapsack](https://developers.google.com/optimization/pack) · [Scheduling](https://developers.google.com/optimization/scheduling) · [OR-Tools samples on GitHub](https://github.com/google/or-tools/tree/stable/ortools) | The API, examples and release notes. Check the version-specific behavior here. |
| 4 | [The CP-SAT Primer (Krupke)](https://d-krupke.github.io/cpsat-primer/) | CP-SAT modeling, parameters, reading the log, LNS, and a MathOpt chapter |
| 5 | [Pyomo docs](https://pyomo.readthedocs.io/en/stable/) · [Pyomo book, 3rd ed.](https://www.osti.gov/servlets/purl/1771935) · [PuLP](https://coin-or.github.io/pulp/) · [HiGHS](https://highs.dev/) | Framework references |
| 5, 9 | [Gurobi docs](https://docs.gurobi.com/projects/optimizer/en/current/) · [Gurobi modeling examples](https://github.com/Gurobi/modeling-examples) · [Gurobi infeasibility tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html) | gurobipy, IIS, feasRelax, multi-objective, numerics guidelines |
| 5, 11 | [Mittelmann benchmarks](https://plato.asu.edu/bench.html) · [MIP Benchmarking: Don't Abuse the Standards (FICO)](https://www.fico.com/blogs/mip-benchmarking-don-t-abuse-standards) · [MIPLIB 2017](https://miplib.zib.de/) | Solver comparison, benchmarking method, test instances |
| 7 | [Mathematical Programming and Capital Budgeting (Princeton archive)](https://www.princeton.edu/~erp/ERParchives/archivepdfs/R14.pdf) · [Large-Scale Multi-Period Optimal Asset Renewal Planning](https://www.researchgate.net/publication/399711038_Large-Scale_Multi-Period_Optimal_Asset_Renewal_Planning_A_Comprehensive_and_Efficient_MILP_Approach) · [numpy-financial](https://numpy.org/numpy-financial/) | Capital budgeting history, utility asset renewal as a MILP, NPV functions |
| 8 | [Mavrotas 2009, AUGMECON](https://doi.org/10.1016/j.amc.2009.03.037) | The augmented ε-constraint method |
| 9 | [Brixius, Detecting the Sources of Model Infeasibility](https://nathanbrixius.com/blog/detecting-the-sources-of-model-infeasibility-using-gurobi) · [Pyomo IIS](https://pyomo.readthedocs.io/en/stable/explanation/analysis/iis.html) · [IP duality and sensitivity (CORE)](https://ideas.repec.org/p/cor/louvrp/431.html) | IIS workflows; what sensitivity means for integer programs |
| 11 | [Hybrid Lagrangian relaxation and Benders decomposition](https://www.research.ed.ac.uk/en/publications/a-hybrid-lagrangian-relaxation-and-benders-decomposition-algorith/) · [Logic-based Benders for time slots (arXiv)](https://arxiv.org/html/2407.02339v3) · [LINDO multi-period planning](https://www.lindo.com/downloads/LINGO_text/Chapter9.pdf) | Decomposition and rolling horizons |
| 12 | [FastAPI](https://fastapi.tiangolo.com/) · [Hypothesis](https://hypothesis.readthedocs.io/) · [moto](https://docs.getmoto.org/) · AWS Batch, Step Functions and Terraform AWS provider documentation | Service, testing and deployment |
| 14 | [OpenSpec (Fission-AI/OpenSpec)](https://github.com/Fission-AI/OpenSpec) | Spec-driven development: living specs, changes with proposals, spec deltas and tasks, validation and archive |

The learner's own background can be used as worked case studies: [consecutive-items-subset-arrangement](https://github.com/msorkhpar/consecutive-items-subset-arrangement) for section 3 (approximation and LP relaxations) and [energy-barrier-problem](https://github.com/msorkhpar/energy-barrier-problem) for section 4 (OR-Tools state modeling). Describe them only as the repositories themselves describe them.

## Authoring order and definition of done

Write the course in five phases. Each phase ends with something a reviewer can read and run.

1. **GridCap first.** Build the dataset generator and its tests before any lesson, because every later example depends on it.
2. **Sections 1–3 and 6.** The modeling spine. Write these first, so every later section can refer back to concepts that already exist.
3. **Sections 4, 5 and 7.** The tools and the domain. Re-run the section 6 examples on each tool.
4. **Sections 8–11.** Multi-objective, diagnostics, determinism and performance, all on GridCap small, medium and large.
5. **Sections 12–13.** The service, the capstone and the practice projects.
6. **Section 14, then 15.** The project-practice feature first, proved on one step; then the three grown projects; then the mock interviews, which cite every section.

Track progress in a `PROGRESS.md` with one row per module, as in the Java course.

**A lesson is done when**

- Every code block and every printed output in it comes from a program that ran.
- It opens with a GridCap scenario, and its headings state its rules.
- It has a quiz of 3–5 questions, plus at least one code or modeling practice. Survey and Prose modules are the exception.
- Every reference is a source it actually opened, from the resource library or found later.
- A reader who didn't write it can follow it, which you check by reviewing it as an outsider.

**A module is done when** all its lessons are done, its examples have tests that pass, and its GridCap milestone (in the section tables above) runs end to end.

**The course is done when** all 57 modules are done, the capstone's 6 milestones pass against the reference solution, and every practice project has a brief, a generator and a grader.

## Decisions

- **Title:** "Integer Programming with Python and Google OR-Tools".
- **Length:** a main path of about 65 hours, with lessons of about 20 minutes. "Going deeper" parts and Stretch practices are optional and come on top.
- **gurobipy:** runnable, using the free size-limited license, so models stay under 2,000 variables and constraints.
- **LLM agents:** not covered.
- **GitHub Copilot:** not covered. No page, practice or quiz mentions Copilot.
- **Growing real projects:** section 14 grows projects one requirement at a time, with before/after code per file and a project practice per step: modules 54–56, plus module 58, which teaches Spec-Driven Development with OpenSpec (lessons 14.4.1–14.4.6).
- **Mock interviews:** the last section (15), module 53, after section 14.
- **Databases:** SQLite is the only database the course uses. Lesson 12.5.3 keeps snapshots and results in S3 and job states in a local SQLite file; no lesson, practice, quiz or citation covers PostgreSQL, RDS or any other cloud database.
- **GPU acceleration:** module 57 in section 11 teaches GPU LP and MIP with HiGHS built with CUDA (cuPDLP-C) and NVIDIA cuOpt, from a separate, optional GPU image. The default images stay CUDA-free and their size is unchanged; only a learner who wants the GPU path downloads the GPU variant. The toolchain knows both variants and picks the GPU one only when it is present and Docker can reach a GPU, falling back to the default image otherwise. Every example and practice runs on the CPU; on the GPU variant the GPU checks run too. Every GPU claim comes from a measured run, with the device class, CUDA versions and the fact that timings depend on the machine stated. The mocks (module 53) carry GPU questions.
- **Practice projects:** a separate Projects track of full multi-file project practices, each with a file explorer, a method-by-method blueprint, a full test suite and an expected-output check (see section 13). Supporting this practice shape in StudyForge is part of the build work, not part of this blueprint.
- **Numbering:** module 50 is unused; sections are numbered 1–15 with no gap.
