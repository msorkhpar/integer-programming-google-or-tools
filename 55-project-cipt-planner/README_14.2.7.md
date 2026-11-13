# 14.2.7 Scenarios, Overrides and Snapshots

Planning season starts, and the requests multiply:

> Finance wants to see the plan with $2.76M held back in 2029. P028 is waiting for a permit, so
> show us the plan without it. The board wants the Valley rebuild P030 in. We need all of these side
> by side, against the same export, and in six months we need to know exactly what each run was
> planned from and what it said.

## Edited Copies of the Export Lose Track of What Was Planned

With `steps/06`, each of these requests means editing a copy of the export: change a budget, set
P028's window to nothing, mark P030 as a must-do. Three problems follow. The edits are invisible: a
copy with P030 marked must-do looks like an export in which P030 always was one. Nothing ties a
plan to the file it came from, so "what was this run planned from" has no answer once the copy is
edited again. And an edit like "mark P030 must-do" changes what the diagnostics of the lesson *Why it failed, why it was deferred: a diagnostics layer*
say: a clash would name `must_P030`, a regulatory rule, when the real cause is a board decision.

## A Scenario Is Data Beside the Export, and an Override Is a Named Row

The design has three parts, each from section 12:

- A **scenario** is a small record: a name, budget changes, overrides and a note saying why
  (section 12, *Scenarios as data: create, copy, optimize*). It never edits the export; `apply(request, scenario)` makes a new `Request`.
- An **override** is a planner's decision about one project: force it in (`force_in`), leave it out
  (`force_out`), or start it in a given year (`fix_start`).
- A **snapshot** is the export exactly as received, stored under the sha256 of its canonical JSON
  in a SQLite file, with every scenario and every run (section 12, *Storing scenarios and results in SQLite*). A run records the
  snapshot's hash, so it can always be traced to the bytes it planned from.

Lesson 6.5.6 and section 12's *Manual overrides as bounds, with an audit trail* wrote overrides as variable bounds: cheap, and presolve removes them. The
planner writes them as rows instead. The choice:

| Override as | For | Against |
| --- | --- | --- |
| bounds on $`x_{i,t}`$ (lesson 6.5.6) | no extra rows; presolve removes fixed variables | the deletion filter of the lesson *Why it failed, why it was deferred: a diagnostics layer* relaxes only rows, so a clashing override would never be named |
| a named row per override (chosen) | the diagnostics name it, as "the scenario funds P030" | one row per override, a handful in practice |

The decision follows from the previous lesson: the diagnostics speak in row names, so anything a
person can change should be a row with a name.

## The Model

The model of the lesson *Two goals: risk against NPV*, with the scenario's budgets and three override rows.

**Sets.** As in the lesson *Two goals: risk against NPV*, plus the scenario's override sets: $`O^{\text{in}} \subseteq P`$,
$`O^{\text{out}} \subseteq P`$, and $`F`$, pairs $`(i, s)`$ of a project and the year it must start.

**Parameters.** As in the lesson *Two goals: risk against NPV*, with $`B_y`$ now the scenario's budget for $`y`$ where it sets
one, and the export's otherwise.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\text{started}(i) &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\text{started}(i) &= 1 && \forall i \in M && \text{(must}_i) \\
\textstyle\sum_{i \in g} \text{started}(i) &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\text{started}(j) - \text{started}(b_1) &= 0 && \forall B \in \mathcal{B},\ j \in B \setminus \{b_1\} && \text{(bundle}_{b_1,j}) \\
\text{started\_by}(c, t) - \text{started\_by}(p(c), t - L_c) &\le 0 && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\; t \le y < t + d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow B_y \text{ from the scenario} \\
\text{R}(x) &\ge \varepsilon && && \text{(risk\_floor)} \\
\text{started}(i) &= 1 && \forall i \in O^{\text{in}} && \text{(in}_i) \quad \leftarrow \text{new} \\
\text{started}(i) &= 0 && \forall i \in O^{\text{out}} && \text{(out}_i) \quad \leftarrow \text{new} \\
\text{started\_by}(i, s) - \text{started\_by}(i, s - 1) &= 1 && \forall (i, s) \in F && \text{(fix}_{i,s}) \quad \leftarrow \text{new}
\end{aligned}
```

$`\text{started\_by}(i, s) - \text{started\_by}(i, s - 1)`$ is $`x_{i,s}`$ when $`s \in T_i`$, so
`fix` says "starts in exactly $`s`$". Written this way, a fixed year outside the window gives the
row $`0 = 1`$, and the diagnostics name it instead of the code raising a `KeyError`.

## The Change, File by File

**`cipt/scenario.py`.** Before: the stub of the lesson *Why it failed, why it was deferred: a diagnostics layer*, `apply` returning the request unchanged.
After, from `steps/07/cipt/scenario.py`:

<!-- snapshot: steps/07/cipt/scenario.py -->
```python
def apply(request: Request, scenario: Scenario) -> Request:
    """The request with the scenario's budgets and overrides; refuses projects the export lacks."""
    named = set(scenario.force_in) | set(scenario.force_out) | set(scenario.fix_start)
    unknown = sorted(named - {p.project_id for p in request.projects})
    if unknown:
        raise ValueError(f"scenario {scenario.name} names unknown projects: {', '.join(unknown)}")
    return replace(request, name=f"{request.name} / {scenario.name}",
                   budget={**request.budget, **scenario.budget},
                   force_in=scenario.force_in, force_out=scenario.force_out, fix_start=dict(scenario.fix_start))
```

`replace` makes a new frozen `Request`; the one loaded from the snapshot is never changed, so one
loaded export can serve every scenario. A scenario is stored as JSON, so `Scenario` turns itself
into a plain dictionary and back. JSON keys are text, so the budget's years become strings on the
way out and integers on the way in. From `steps/07/cipt/scenario.py`:

<!-- snapshot: steps/07/cipt/scenario.py -->
```python
    def to_dict(self) -> dict:
        data = asdict(self)
        data["budget"] = {str(y): v for y, v in self.budget.items()}
        return {**data, "force_in": list(self.force_in), "force_out": list(self.force_out)}

    @classmethod
    def from_dict(cls, data: dict) -> "Scenario":
        return cls(name=data["name"], budget={int(y): v for y, v in data["budget"].items()},
                   force_in=tuple(data["force_in"]), force_out=tuple(data["force_out"]),
                   fix_start=dict(data["fix_start"]), note=data["note"])
```

 `diff(base, other)` in the same file lists the projects
selected, deferred and shifted between two plans (lesson 9.3.3).

**`cipt/rules.py`.** One rule, `overrides(built)`, the last of `RULES`, and the page leaves its
code to the practice. It writes the three new row families of the model above from the request's
override fields, each row through `built.add` and the helpers `started` and `started_by` of the
lesson *Business rules: must-dos, bundles, parents and alternatives*:

- $`\text{in}_i`$ for each project id in `request.force_in`, named `in_<id>`;
- $`\text{out}_i`$ for each project id in `request.force_out`, named `out_<id>`;
- $`\text{fix}_{i,s}`$ for each entry of `request.fix_start`, a dict from project id to the year
  $`s`$, named `fix_<id>_<year>`, written as the difference of two `started_by` sums, as the model
  block does, never as a lookup of `x[id, s]`.

The fixed starts are added in project order, so their rows come out in the same order on every
run, whatever order the scenario listed them in.

**`cipt/data.py`.** `Request` gains `force_in`, `force_out` and `fix_start`, all empty by default.
They are not read from the export: only `apply` sets them.

**`cipt/diagnose.py`.** `describe` gains three branches, `in`, `out` and `fix`, as the lesson *Why it failed, why it was deferred: a diagnostics layer*
predicted every new rule would need.

**`cipt/store.py`.** Before: a stub with the schema and empty methods. After, the snapshot is
stored under its hash and checked against it when read. From `steps/07/cipt/store.py`:

<!-- snapshot: steps/07/cipt/store.py -->
```python
def canonical(raw: dict) -> str:
    return json.dumps(raw, sort_keys=True, separators=(",", ":"))


def content_hash(raw: dict) -> str:
    return hashlib.sha256(canonical(raw).encode("utf-8")).hexdigest()
```

<!-- snapshot: steps/07/cipt/store.py -->
```python
    def save_snapshot(self, raw: dict) -> str:
        digest = content_hash(raw)
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO snapshot VALUES (?, ?)", (digest, canonical(raw)))
        return digest

    def snapshot(self, digest: str) -> dict:
        (body,) = self.db.execute("SELECT body FROM snapshot WHERE hash = ?", (digest,)).fetchone()
        raw = json.loads(body)
        if content_hash(raw) != digest:
            raise ValueError(f"snapshot {digest[:12]} does not match its hash")
        return raw
```

`canonical` is JSON with sorted keys (`sort_keys=True`) and no spaces (`separators=(",", ":")`
instead of the default `", "` and `": "`), so equal exports give equal bytes and equal hashes
(lesson 10.2.4). `INSERT OR IGNORE` makes saving the same export twice a no-op: the hash is the
key. `with self.db:` commits on success and rolls back on an error.

The rest of the store saves a scenario beside its snapshot, loads it back, plans it and reads the
runs. From `steps/07/cipt/store.py`:

<!-- snapshot: steps/07/cipt/store.py -->
```python
    def save_scenario(self, scenario: Scenario, snapshot: str) -> None:
        with self.db:
            self.db.execute("INSERT OR REPLACE INTO scenario VALUES (?, ?, ?)",
                            (scenario.name, snapshot, canonical(scenario.to_dict())))

    def scenario(self, name: str) -> tuple[Scenario, str]:
        body, snapshot = self.db.execute("SELECT body, snapshot FROM scenario WHERE name = ?", (name,)).fetchone()
        return Scenario.from_dict(json.loads(body)), snapshot

    def run(self, name: str) -> Plan:
        """Plan a stored scenario from its snapshot, and store the run."""
        scenario, snapshot = self.scenario(name)
        plan = solve(apply(load_request(self.snapshot(snapshot)), scenario))
        with self.db:
            self.db.execute("INSERT INTO run (scenario, snapshot, status, npv, risk, starts) VALUES (?, ?, ?, ?, ?, ?)",
                            (name, snapshot, plan.status, plan.npv, plan.risk, canonical(plan.starts)))
        return plan

    def runs(self, name: str) -> list[Plan]:
        found = self.db.execute("SELECT status, npv, risk, starts FROM run WHERE scenario = ? ORDER BY id", (name,))
        return [Plan(status=s, starts=json.loads(starts), objective=npv, npv=npv, risk=risk)
                for s, npv, risk, starts in found]
```

`save_scenario` stores the scenario's canonical JSON under its name; `INSERT OR REPLACE` makes a
second save under the same name replace the first. `scenario(name)` returns the stored scenario and
its snapshot's hash. `run(name)` loads both, plans the scenario's request from the snapshot's
bytes, and stores the run with the snapshot's hash and the plan's starts as canonical JSON.
`runs(name)` returns every stored run of a scenario as a list of `Plan`s, oldest first
(`ORDER BY id`), each with its status, starts, NPV and risk, and the NPV as its objective.

**`cipt/solve.py` and `cipt/trust.py`** gain the stubs for the lesson *Trust at scale: determinism harness, golden tests, warm starts*.
`trust.py` is new; no code of this step imports it, and in this lesson's practice it already
holds these stubs.

## Scenarios Run Side by Side Against One Snapshot

`scenarios_small.py` stores GridCap small (a fictional utility) once, saves four scenarios and runs
each, then the base again:

```text
snapshot 54acf05890b5, saved twice: True
scenario      NPV ($k)   risk ($k)   selected   deferred   shifted
base            24,260     3,709.1          0          0         0
cut 2029        23,086     3,865.4          2          3         6
hold P028       23,390     3,137.7          3          5         5
P030 first      23,390     3,137.7          3          5         5
P030 first, selected: P002, P030, P036; deferred: P001, P005, P016, P028, P031
P030 first, shifted: P011 2031->2029, P015 2029->2030, P017 2030->2031, P021 2029->2028, P029 2031->2030
base runs stored: 2, same plan: True; hold P028 and P030 first give one plan: True
tables: snapshot 1, scenario 4, run 5
```

Two different requests gave one plan. Holding P028 frees money that the best use is P030, and
forcing P030 in pushes P028 out, so both scenarios end at the same plan, worth $870k less than the
base. That is the same $870k the lesson *Why it failed, why it was deferred: a diagnostics layer* priced for P030: two questions, one answer, and the
scenario table shows it without anyone having to notice.

"cut 2029" gives up $1,174k of NPV and happens to remove $156k more risk than the base; risk is
not what this plan maximizes, so that is a side effect of the projects chosen, not a goal. Six
projects shift years.

An override that clashes with a rule is named like any rule:

```text
No plan meets these 3 rules together; drop or change any one of them:
  alt_G030: at most one of P030, P031
  in_P030: the scenario funds P030
  in_P031: the scenario funds P031
```

Had `force_in` been a bound, the filter could not have named it, and the message would have named
only `alt_G030`, a rule nobody can change.

## Tests Check the Store by Its Contract, Not Its Tables

From `steps/07/tests/test_scenarios.py`, the snapshot's tamper check:

<!-- snapshot: steps/07/tests/test_scenarios.py -->
```python
def test_changed_snapshot_is_refused(tmp_path):
    store = Store(tmp_path / "cipt.db")
    digest = store.save_snapshot(base())
    with sqlite3.connect(tmp_path / "cipt.db") as db:
        db.execute("UPDATE snapshot SET body = replace(body, '300', '900')")
    with pytest.raises(ValueError, match="does not match"):
        store.snapshot(digest)
```

The test edits the file behind the store's back, as a person with a database tool could, and
expects the read to refuse it. The stub in `steps/06` kept the schema, so this test fails there on
"did not raise", not on a missing table.

```text
14.2.7: 9 tests added; on step 06, 9 fail on an assertion; on step 07, 50 of 50 pass
  test_force_out_drops_a_project
    before: assert ('A', 'B') == ('B', 'C')
    after:  passed
  test_force_in_funds_a_low_value_project
    before: assert ('A', 'B') == ('A', 'C')
    after:  passed
  test_fix_start_pins_the_year
    before: assert 2027 == 2028
    after:  passed
  test_budget_change_replaces_one_year
    before: assert {'A': 2027, 'B': 2028} == {'A': 2027}
    after:  passed
  test_clashing_override_is_named_in_the_conflict
    before: assert None == ['alt_G', 'in_B', 'must_A']
    after:  passed
  test_diff_reports_selected_deferred_and_shifted
    before: assert ((), ()) == (('C',), ('B',))
    after:  passed
  test_snapshot_is_stored_under_its_hash
    before: assert '' == 'c4eb3d1286bd...b68b1a4cae647'
    after:  passed
  test_changed_snapshot_is_refused
    before: Failed: DID NOT RAISE ValueError
    after:  passed
  test_run_is_stored_and_read_back
    before: assert [] == [(('B', 'C'), 250)]
    after:  passed
```

## Storage Added Two Files and Kept the Model Untouched

```text
14.2.7: steps/06 -> steps/07
  package lines 516 -> 616, functions 49 -> 63, tests 41 -> 50
  most branches: goals.frontier (10) -> diagnose.describe (11)
  data.py       106 ->  109
  diagnose.py    76 ->   83
  rules.py       46 ->   55
  scenario.py    24 ->   47
  solve.py       38 ->   41
  store.py       34 ->   60
  trust.py        0 ->   29
```

`model.py` did not change again. Everything a scenario changes reaches the model through the
`Request` and one rule. `describe` is now the most-branched function: eleven paths, one per row
kind. It is the one place where adding a rule means editing a second file, and a table from prefix
to sentence would end that if a twelfth rule comes.

**Practice.** This lesson's project practice starts from `steps/06`, the whole package. It is
graded by the tests in the practice's `tests/` folder and by a check that `main.py`, which plans the
demo export, prints what the practice's `expected/report.txt` holds. This step's `main.py` also
compares the demo plan with a scenario that adds $1,000k to the budgets of 2028 and 2029, after
the frontier section: an empty line, `scenario <name>: NPV $<base npv>k -> $<scenario npv>k`, then
`  selected <ids>; deferred <ids>` (`none` for an empty list), then one line
`  shifted <id> <base start> -> <scenario start>` per shifted project.

<!-- practice 1 -->

## Summary

- **Edited copies of the export lose track of what was planned**, and make the diagnostics name
  the wrong rule.
- **A scenario is data beside the export, and an override is a named row**, so a clashing
  override is named in planner language.
- **A snapshot is stored under the hash of its canonical JSON**, and a changed byte is refused when
  it is read.
- **Scenarios run side by side against one snapshot**; on GridCap small two different requests led
  to one plan.

## Reference

| Name | Meaning |
| --- | --- |
| `Scenario` | name, `budget`, `force_in`, `force_out`, `fix_start`, `note` |
| `apply(request, scenario)` | a new `Request`; refuses projects the export lacks |
| `in_P030`, `out_P028`, `fix_P013_2029` | the override rows |
| `Store` | SQLite tables `snapshot`, `scenario`, `run` |
| `content_hash(raw)` | sha256 of the canonical JSON |
| `diff(base, other)` | selected, deferred and shifted projects |

**Further reading:** [MathOpt `model.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/model.py) (each named row added by `add_linear_constraint`, the overrides included); [MathOpt `linear_constraints.py` (OR-Tools source)](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/linear_constraints.py) (the bounds the deletion filter relaxes, which is why an override that is a row can be named).

## Challenges

1. A scenario fixes P013 to start in 2026, outside the plan. Predict the conflict the planner
   prints, then run it.
2. Add a `region` column filter to `Scenario`: "fund nothing in Coast". Is that an override, a
   budget change, or a new rule?
3. Two planners save scenarios with the same name. What does `save_scenario` do, and should it?

## Design Note: The Snapshot Is the Unit of Truth

The store keeps the export as received, not the `Request` the loader built from it. A loader bug
fixed next year would change the `Request`, but not the snapshot, so an old run can be replayed
against the same bytes with the new code, and the difference is the fix. Storing the `Request`
instead would freeze the bug into every record.

## The Full Programs

**scenarios_small.py.** Stores GridCap small once, saves and runs four scenarios with `steps/07`,
compares each plan with the base, and names a clashing pair of overrides. *Try:* add a scenario that
fixes P030 to start in 2030 and predict its NPV before running.

- Program: [scenarios_small.py](src/scenarios_small.py)

**ledger.py, code_size.py.** The test ledger and the size table for step 07.

- Program: [ledger.py](src/ledger.py)
- Program: [code_size.py](src/code_size.py)
