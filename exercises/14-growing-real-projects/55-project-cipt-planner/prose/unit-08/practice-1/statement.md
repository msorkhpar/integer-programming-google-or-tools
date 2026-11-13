The planner is now used for the real portfolio, GridCap medium in this course: 400 projects over
ten years (fictional, like all GridCap data). Audit and the planning lead sent the last requests:

> Audit: if we run the same export twice we must get the same plan, and every run must say what it
> was planned from and with what. Prove it.
>
> Planning lead: the rule tests are good, but last month a change to the window code moved projects
> and no test noticed. And each run takes half a minute now; next cycle starts from this cycle's
> plan, so can the solver start from it too?

You start from the planner with scenarios and snapshots. Identify a plan by a digest of its content,
rerun an export from scratch and show whether the runs agree, and record for each run what it was
planned from and with which solver and settings. Check today's plan of a fixed export against a
reviewed golden plan and list every project whose start moved, including one the golden plan never
funded. Let a solve start from last cycle's plan, keeping only the starts the new model still has,
and give the same plan as a solve from nothing.

A plan's canonical JSON is that of the store: sorted keys, no spaces after `,` and `:`. A golden
file is one JSON object with the keys `input` (the export's content hash), `npv`, `starts` and
`status`, written with sorted keys, an indent of one space and a final newline. When the export's
hash differs from the golden file's `input`, the check returns the single line
`input changed: golden <first 12 hex digits>, now <first 12 hex digits>`. A hint reaches HiGHS as
`mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values=...)])`, passed
to `mathopt.solve` as `model_params`, with the variables of this model as keys.

Run's report gains a line: `main.py` now plans the demo export three times and says whether the
plans agree. After the scenario section it prints an empty line, then
`3 runs, same plan: <True or False>, plan digest <12 hex digits>`, the digits being the start of
the first run's plan digest. Submit runs every test in `tests/`, the earlier steps'
included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `plan_digest` in `cipt/trust.py`

```python
def plan_digest(plan: Plan) -> str
```

- **Contract.** Returns the sha256 hex digest of the plan's canonical JSON, status and starts only.
- **Modeling idea.** Two runs agree exactly when their plan digests do.
- **Taught in** [10.2.5 Building the Deterministic Run Harness](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-05/10.2.5-building-the-deterministic-run-harness.unit.html).

#### `harness` in `cipt/trust.py`

```python
def harness(raw: dict, runs: int = 3, scenario: Scenario = Scenario("base")) -> Harness
```

- **Contract.** Plans the same export, under a scenario ('base' by default), `runs` times from scratch, and returns a Harness of the plans' digests.
- **Modeling idea.** A determinism harness reruns from scratch and compares digests, not objective values.
- **Taught in** [10.2.5 Building the Deterministic Run Harness](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-05/10.2.5-building-the-deterministic-run-harness.unit.html).

#### `manifest` in `cipt/trust.py`

```python
def manifest(raw: dict, scenario: Scenario, plan: Plan) -> dict
```

- **Contract.** Returns what a run depended on: the export's content hash as input, the scenario as a dictionary, the solver (name HIGHS, the OR-Tools version, the thread count), the plan's digest and its NPV rounded to cents.
- **Modeling idea.** A run is reproducible when its manifest pins the input, the settings and the solver.
- **Taught in** [10.2.4 Versioned Input Snapshots, Pinned Solvers and Run Manifests](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-04/10.2.4-versioned-input-snapshots-pinned-solvers-and-run-manifests.unit.html).

#### `check_golden` in `cipt/trust.py`

```python
def check_golden(raw: dict, path: str | Path) -> list[str]
```

- **Contract.** Returns every way today's plan of the export differs from the golden file: a changed input alone when the hashes differ (`input changed: golden <12 hex digits>, now <12 hex digits>`); otherwise, in this order, `status <golden> -> <now>` when the status differs, each project whose start differs as `<id>: start <golden> -> <now>` over the projects of both plans in id order (`None` for a project a plan does not fund), and `npv <golden> -> <now>` (whole $k, thousands commas) when the NPV moves by more than 0.5. Empty when they agree.
- **Modeling idea.** A golden test pins a reviewed plan of a fixed input, so a change that moves the plan fails until someone reviews it.
- **Taught in** [12.3.3 Golden Datasets and Regression Tests](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-03/12.3.3-golden-datasets-and-regression-tests.unit.html).

#### `write_golden` in `cipt/trust.py`

```python
def write_golden(raw: dict, path: str | Path) -> None
```

- **Contract.** Writes today's plan of the export as the golden file: one JSON object with the keys input (the export's content hash), npv, starts and status, sorted, indented by one space, with a final newline.
- **Modeling idea.** The golden plan is written by the code and reviewed by a person.
- **Taught in** [12.3.3 Golden Datasets and Regression Tests](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-03/12.3.3-golden-datasets-and-regression-tests.unit.html).

#### `hint_values` in `cipt/solve.py`

```python
def hint_values(built: Built, previous: Plan) -> dict[tuple[str, int], float]
```

- **Contract.** Returns a value for every variable of the model: 1.0 where the previous plan starts that project in that year, else 0.0. A previous start the model has no variable for is dropped.
- **Modeling idea.** A MIP start must name only variables the new model has.
- **Taught in** [11.2.1 MIP Starts From Last Cycle's Plan](../../../../11-performance-at-scale/43-warm-starts-and-tuning/units/unit-01/11.2.1-mip-starts-from-last-cycles-plan.unit.html).

#### `solve` in `cipt/solve.py`

```python
def solve(request: Request, previous: Plan | None = None) -> Plan
```

- **Contract.** Plans a request; with a previous plan, hands HiGHS the hint as a starting solution.
- **Modeling idea.** A warm start changes where the search begins, never the optimal plan.
- **Taught in** [11.2.1 MIP Starts From Last Cycle's Plan](../../../../11-performance-at-scale/43-warm-starts-and-tuning/units/unit-01/11.2.1-mip-starts-from-last-cycles-plan.unit.html).

#### `warm_solve` in `cipt/trust.py`

```python
def warm_solve(raw: dict, previous: Plan) -> Plan
```

- **Contract.** Plans the export starting from last cycle's plan.
- **Modeling idea.** Next cycle starts from this cycle's plan.
- **Taught in** [11.2.1 MIP Starts From Last Cycle's Plan](../../../../11-performance-at-scale/43-warm-starts-and-tuning/units/unit-01/11.2.1-mip-starts-from-last-cycles-plan.unit.html).
