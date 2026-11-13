Planning season starts, and the requests multiply:

> Finance wants to see the plan with $2.76M held back in 2029. P028 is waiting for a permit, so
> show us the plan without it. The board wants the Valley rebuild P030 in. We need all of these side
> by side, against the same export, and in six months we need to know exactly what each run was
> planned from and what it said.

You start from the planner with diagnostics. Add scenarios: a named set of budget changes and
overrides (projects forced in, forced out, or fixed to a start year) kept as data beside the
export, never written into it. Each override becomes a named row, so a conflict can name it. Two
plans are compared by the projects selected, deferred and shifted. Store each export once, as a
snapshot under the hash of its content, refuse a stored snapshot whose content no longer matches
its hash, and store each run with the snapshot it was planned from, in one SQLite file.

The canonical form of an export is its JSON with sorted keys and no spaces after `,` and `:`; the
snapshot's hash is the sha256 hex digest of that text in UTF-8. Saving a scenario under a name that
is already stored replaces it, and the runs of a scenario come back as `Plan`s, oldest first.

Run's report gains a section: `main.py` now compares the demo plan with a scenario named
`more money` that adds $1,000k to the budgets of 2028 and 2029. After the frontier section it
prints an empty line, then `scenario more money: NPV $<base npv>k -> $<scenario npv>k` (whole $k,
thousands commas), then `  selected <ids>; deferred <ids>` with the ids joined by a comma and a
space, or `none`, then one line `  shifted <id> <base start> -> <scenario start>` per project that
starts in another year.

`cipt/trust.py` holds the next lesson's stubs, as the reference has them; no code of this step
imports it, so leave it as it is. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `apply` in `cipt/scenario.py`

```python
def apply(request: Request, scenario: Scenario) -> Request
```

- **Contract.** Returns the request with the scenario's budget changes laid over its budgets, its overrides (force_in, force_out, fix_start) set, and its name `<request> / <scenario>`. Refuses a scenario that names a project the export does not have.
- **Modeling idea.** A scenario never edits the export: it is data beside it, applied to a copy.
- **Taught in** [12.1.1 Scenarios as Data: Create, Copy, Optimize](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-01/12.1.1-scenarios-as-data-create-copy-optimize.unit.html).

#### `overrides` in `cipt/rules.py`

```python
def overrides(built: Built) -> None
```

- **Contract.** Adds a row `in_<id>` (started once) per forced-in project, `out_<id>` (never started) per forced-out project, and `fix_<id>_<year>` (started in exactly that year) per fixed start.
- **Modeling idea.** An override is a named row, so the diagnostics can name an override that clashes with a rule.
- **Taught in** [6.5.6 Manual Overrides as Fixed Bounds](../../../../06-formulation-craft/27-dependencies-and-groups/units/unit-06/6.5.6-manual-overrides-as-fixed-bounds.unit.html).

#### `describe` in `cipt/diagnose.py`

```python
def describe(request: Request, name: str) -> str
```

- **Contract.** Also describes `in_<id>`, `out_<id>` and `fix_<id>_<year>`: `the scenario funds <id>`, `the scenario leaves <id> out`, `the scenario starts <id> in <year>`.
- **Modeling idea.** A new kind of row needs words the planners read.
- **Taught in** [9.1.6 Turning an IIS Into a Planner Message](../../../../09-diagnostics-and-explainability/37-infeasibility/units/unit-06/9.1.6-turning-an-iis-into-a-planner-message.unit.html).

#### `diff` in `cipt/scenario.py`

```python
def diff(base: Plan, other: Plan) -> Diff
```

- **Contract.** Returns the projects funded only in the other plan (selected), those funded only in the base plan (deferred), and those funded in both with different starts (shifted, as id, base start, other start).
- **Modeling idea.** Planners compare plans by selected, deferred and shifted projects.
- **Taught in** [9.3.3 Scenario Diffs: Selected, Deferred, Shifted](../../../../09-diagnostics-and-explainability/39-explaining-decisions/units/unit-03/9.3.3-scenario-diffs-selected-deferred-shifted.unit.html).

#### `canonical` in `cipt/store.py`

```python
def canonical(raw: dict) -> str
```

- **Contract.** Returns the export as JSON with sorted keys and no spaces, so equal exports give equal text.
- **Modeling idea.** A hash identifies content only when the content is written one way.
- **Taught in** [12.1.4 Storing Scenarios and Results in SQLite](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-04/12.1.4-storing-scenarios-and-results-in-sqlite.unit.html).

#### `content_hash` in `cipt/store.py`

```python
def content_hash(raw: dict) -> str
```

- **Contract.** Returns the sha256 hex digest of the canonical JSON.
- **Modeling idea.** A snapshot is stored under the hash of its content.
- **Taught in** [12.1.4 Storing Scenarios and Results in SQLite](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-04/12.1.4-storing-scenarios-and-results-in-sqlite.unit.html).

#### `snapshot` in `cipt/store.py`

```python
def snapshot(self, digest: str) -> dict
```

- **Contract.** Returns the stored export for a hash, and raises ValueError ('does not match') when the stored body no longer hashes to that value.
- **Modeling idea.** Check the content against its hash on every read, so a changed byte is caught.
- **Taught in** [12.1.4 Storing Scenarios and Results in SQLite](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-04/12.1.4-storing-scenarios-and-results-in-sqlite.unit.html).

#### `run` in `cipt/store.py`

```python
def run(self, name: str) -> Plan
```

- **Contract.** Plans a stored scenario from its stored snapshot, stores the run (scenario, snapshot hash, status, NPV, risk, starts) and returns the plan.
- **Modeling idea.** A run is traceable when it records the snapshot it planned from.
- **Taught in** [12.1.4 Storing Scenarios and Results in SQLite](../../../../12-engineering-the-optimization-service/45-scenario-workflow/units/unit-04/12.1.4-storing-scenarios-and-results-in-sqlite.unit.html).
