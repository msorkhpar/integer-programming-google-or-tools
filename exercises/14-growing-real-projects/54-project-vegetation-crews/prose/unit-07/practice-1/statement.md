GridCap's vegetation planner now runs the planner every Monday, and wrote:

> I ran the plan twice this morning on the same data, to check something, and got two different plans,
> with different risk totals. Which one did we send the crews? When the regulator asks why C27 waited
> until September, I need to rerun the plan and get the *same* plan, and I need to know that next
> month's code change did not quietly change it.

You start from the planner with overrides and explanations. Make the search repeat: the same season
gives the same plan on every run, on any machine, for one OR-Tools version. Give each plan a record
that names what it was planned from (a fingerprint of the season and the overrides), the solver and
its settings, and what it decided, written one way so two records can be compared as text; and let
the command line print it with `--record`. The tests compare today's records of the tiny and the
small seasons with reviewed golden files in `tests/golden/`.

**`main.py`.** Remove the line that sets `planner.WORKERS = 1`: the planner's settings now repeat the
search by themselves. After the overrides' sections, print an empty line and
`input sha256 <fingerprint>, records of two runs identical: <yes or no>`, where `<fingerprint>` is
the first 12 hex digits of the fingerprint of the tiny season (seed 54) with no overrides, and the
two records are `dumps(plan_record(raw, make_plan(season)))` of two plans of that season made one
after the other in the same process.

Run's report gains that line, as `expected/report.txt` shows. Submit runs every test in `tests/`,
the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `make_plan` in `vegcrew/planner.py`

```python
def make_plan(season: Season, overrides: tuple[Override, ...] = ()) -> Plan
```

- **Contract.** As before, with the solver set from SETTINGS, a module constant: 4 workers that interleave instead of racing, random_seed 7, and max_deterministic_time 10.0 in place of a limit in seconds.
- **Modeling idea.** Determinism is a setting: interleaved workers, a seed and a limit on deterministic time repeat the same search on every run.
- **Taught in** [4.6.3 Deterministic Time, Seeds and Reproducible Runs](../../../../04-google-or-tools-in-depth/17-cpsat-tuning-and-diagnostics/units/unit-03/4.6.3-deterministic-time-seeds-and-reproducible-runs.unit.html).

#### `canonical` in `vegcrew/record.py`

```python
def canonical(value) -> str
```

- **Contract.** Returns a value as JSON with sorted keys and no spaces, so equal values give equal text.
- **Modeling idea.** A hash identifies content only when the content is written one way.
- **Taught in** [10.2.5 Building the Deterministic Run Harness](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-05/10.2.5-building-the-deterministic-run-harness.unit.html).

#### `fingerprint` in `vegcrew/record.py`

```python
def fingerprint(raw: dict, overrides: tuple[Override, ...] = ()) -> str
```

- **Contract.** Returns the SHA-256 hex digest of the canonical JSON of {'season': raw, 'overrides': each override's fields as a dictionary}.
- **Modeling idea.** Equal inputs give equal fingerprints, and any change to the season or the overrides changes it.
- **Taught in** [10.2.5 Building the Deterministic Run Harness](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-05/10.2.5-building-the-deterministic-run-harness.unit.html).

#### `plan_record` in `vegcrew/record.py`

```python
def plan_record(raw: dict, plan: Plan, overrides: tuple[Override, ...] = ()) -> dict
```

- **Contract.** Returns the record of a plan: input_sha256, the OR-Tools version (ortools.__version__), the settings, status, risk_carried, cost, the trims sorted by circuit id as `<cid> on <crew> weeks <first>-<last>`, and the explanation as a list.
- **Modeling idea.** A record names the input, the solver and its settings, so a difference points at its cause.
- **Taught in** [10.2.5 Building the Deterministic Run Harness](../../../../10-numerics-and-determinism/41-determinism-and-reproducibility/units/unit-05/10.2.5-building-the-deterministic-run-harness.unit.html).

#### `dumps` in `vegcrew/record.py`

```python
def dumps(record: dict) -> str
```

- **Contract.** Returns the record as the text stored and compared: keys sorted, an indent of one, and a newline at the end.
- **Modeling idea.** Two runs gave the same plan exactly when their records are equal byte for byte.
- **Taught in** [12.3.3 Golden Datasets and Regression Tests](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-03/12.3.3-golden-datasets-and-regression-tests.unit.html).

#### `main` in `vegcrew/__main__.py`

```python
def main(argv: list[str] | None = None) -> None
```

- **Contract.** With --record, prints the plan's record as dumps writes it, adding no newline of its own; without it, the report as before.
- **Modeling idea.** A golden file is written by the code itself and reviewed by a person.
- **Taught in** [12.3.3 Golden Datasets and Regression Tests](../../../../12-engineering-the-optimization-service/47-testing-optimization-code/units/unit-03/12.3.3-golden-datasets-and-regression-tests.unit.html).
