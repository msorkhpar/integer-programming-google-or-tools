# 12.4.3 Result Schemas Planners Can Consume

The planning tool's developers now poll jobs and fetch results, and they start building screens: a
plan table, a chart of spend against budget by year, a banner with the job's status. Within a week
they have questions the API cannot answer. Is `npv` in dollars or thousands? Why are the years
strings? What does a missing `gap` mean, and can `status` say anything other than the values they
have seen? A result is read by another team's code, which cannot ask. This lesson writes the result
as a schema: every field named, typed and described, the rules between fields enforced before a
result leaves the service, and a way to change it later without breaking the tool. (GridCap is
fictional; no number in it is real.)

## The Model

The jobs solve the model of lessons 12.4.1 and 12.4.2, restated here whole; this lesson adds no row.
What it adds is a report of the model's own expressions: the spend of each year, the left side of
$`\text{budget}_y`$, is what `spend_by_year` returns next to $`B_y`$.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work ($k); $`B_y`$, the budget of
year $`y`$ ($k), the request's value if it sends one.

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$: project $`i`$
starts in year $`t`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\underbrace{\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t}}_{\text{spend}_y} &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow \text{reported per year}
\end{aligned}
```

In the result, `spend` is $`\text{spend}_y`$ evaluated on the plan, `budget` is $`B_y`$, and
`headroom` is $`B_y - \text{spend}_y`$. `npv` is the objective's value, `bound` the solver's bound on
it, and `gap` is $`\max(0,\ \text{bound} - \text{npv}) / \max(|\text{npv}|,\ 1)`$, lesson 12.4.2's
formula: 1 is the smallest divisor, so a plan worth 0 still has a gap, and a bound below the value
gives a gap of 0.

## A Result Carries the Plan, the Money by Year, the Value, the Gap, the Status and a Message

`schemas.py` defines the result as three pydantic models: one row per funded project, one row per
year, and the result around them.

```python
class ProjectStart(BaseModel):
    project_id: str
    start_year: int
    program: str
    region: str
    capex: int = Field(description="total cost over the project's years of work, $k")
    npv: int = Field(description="NPV of the project at this start year, $k")

class YearSpend(BaseModel):
    year: int
    spend: int = Field(description="what the plan spends this year, $k")
    budget: int = Field(description="the budget the job ran with, $k")
    headroom: int = Field(description="budget minus spend, $k")

class PlanResult(BaseModel):
    schema_version: Literal["1.0"] = Field(default="1.0", description="changes only when a field changes meaning")
    job_id: str = Field(description="the id POST /jobs returned")
    snapshot: str = Field(description="sha256 of the request, the portfolio and the solver settings")
    status: Literal["optimal", "time_limit", "infeasible", "failed"] = Field(description="how the solve ended")
    message: str = Field(description="one paragraph for the planner, written from the fields below")
    npv: float | None = Field(description="NPV of the plan, $k; null when there is no plan")
    bound: float | None = Field(description="no plan is worth more than this, $k; null when unknown")
    gap: float | None = Field(ge=0, description="max(0, bound - npv) / max(|npv|, 1); null when there is no plan")
    plan: list[ProjectStart] = Field(description="one row per funded project; empty when there is no plan")
    spend_by_year: list[YearSpend] = Field(description="one row per year; empty when there is no plan")
```

Why each field is there, and in this shape:

- **`status` and `message` come first in meaning.** A planner reads the status to know what kind of
  answer this is (lesson 12.4.2's table) and the message for what to do. `Literal` fixes the four
  values, so a tool can switch on them and know the list is complete.
- **`npv`, `bound` and `gap` travel together.** NPV alone hides whether the plan is proven; lesson
  9.3.4 shows finance reading NPV with its status and gap. `bound` lets a tool show the best value
  still possible.
- **The plan is a list of rows, not a dict.** Each row repeats what a table needs (program, region,
  cost, value) so the tool joins nothing. Lesson 12.4.1 showed `dict[int, ...]` keys arriving as
  strings; rows keep `year` an integer and the rows in order.
- **`spend_by_year` puts each year's spend next to its budget.** The headroom is the first number a
  planner asks about after a budget cut. Every number is computed from the data by `spend_of`, not
  read back from the model, so the check is independent of the solve (lesson 9.3.4).
- **`snapshot` and `job_id` tie the result to its inputs.** The snapshot is lesson 7.1.3's id: a
  hash of the request, the portfolio's content hash and the solver settings, so two results with
  equal snapshots came from equal inputs. `schema_version` is the subject of the last section.
- **Every field has a description with its unit.** Money is in $k everywhere, and the description
  says so, in the published schema, where the tool's developers will look.

`to_result` builds one from a finished job:

```python
def to_result(job_id: str, request: JobRequest, outcome: Outcome) -> PlanResult:
    pf = portfolio(request.portfolio)
    budget = {**pf.budget, **request.budget}
    plan = [ProjectStart(project_id=pid, start_year=t, program=pf.project(pid).program,
                         region=pf.project(pid).region, capex=pf.project(pid).capex, npv=pf.project(pid).npv[t])
            for pid, t in outcome.starts.items()]
    spend = spend_of(pf, outcome.starts) if outcome.npv is not None else {}
    years = [YearSpend(year=y, spend=spend[y], budget=budget[y], headroom=budget[y] - spend[y]) for y in spend]
    return PlanResult(job_id=job_id, snapshot=snapshot(request), status=outcome.status, message=outcome.message,
                      npv=outcome.npv, bound=outcome.bound, gap=outcome.gap, plan=plan, spend_by_year=years)
```

`GET /jobs/{id}/result` (lesson 12.4.2) returns it, and FastAPI converts it to JSON. `result_json.py`
fetches the small portfolio's result, and one for the 2030-31 cut that leaves must-do P017 no start
(the plan list is cut to two rows for the page):

```text
{
 "schema_version": "1.0",
 "job_id": "job-1",
 "snapshot": "136f3589852f48787b45ef19a68d30364e9a0341f989692139ba2186f4970b5f",
 "status": "optimal",
 "message": "Best plan found and proven: NPV $24,260k.",
 "npv": 24260.0,
 "bound": 24260.0,
 "gap": 0.0,
 "plan": [
  {
   "project_id": "P001",
   "start_year": 2028,
   "program": "transmission",
   "region": "Plains",
   "capex": 2640,
   "npv": 1401
  },
  {
   "project_id": "P003",
   "start_year": 2031,
   "program": "vegetation",
   "region": "Valley",
   "capex": 140,
   "npv": 107
  },
  "... 25 more"
 ],
 "spend_by_year": [
  {
   "year": 2027,
   "spend": 8750,
   "budget": 8890,
   "headroom": 140
  },
  {
   "year": 2028,
   "spend": 7970,
   "budget": 8120,
   "headroom": 150
  },
  {
   "year": 2029,
   "spend": 8630,
   "budget": 8760,
   "headroom": 130
  },
  {
   "year": 2030,
   "spend": 8560,
   "budget": 8610,
   "headroom": 50
  },
  {
   "year": 2031,
   "spend": 7720,
   "budget": 7850,
   "headroom": 130
  }
 ]
}
{
 "schema_version": "1.0",
 "job_id": "job-2",
 "snapshot": "1e358089cc0556e945bdb1c5f46e705995dad3b36605e080d0e71f661ce920e8",
 "status": "infeasible",
 "message": "No plan meets every rule and budget. The must-do projects and the budgets cannot all be met; check the budgets you changed first.",
 "npv": null,
 "bound": null,
 "gap": null,
 "plan": [],
 "spend_by_year": []
}
```

The proven plan funds 27 projects for $24,260k, gap 0, and stays within every year's budget, with
2030 the tightest at $50k of headroom. The infeasible result has the same fields, with `null` where
there is no number and empty lists where there are no rows. A tool draws both with the same code;
it never has to check whether a key exists.

The message is written from the fields, never typed separately (lesson 9.3.4's rule): the NPV in
"Best plan found and proven: NPV $24,260k." is `npv`, formatted. An infeasible result's message
says what to check, not which rows conflicted; lesson 9.1.6 turns an IIS into a message that names
the projects and rules, and a service that runs it would put that text here.

## Every Field Has One Meaning, and the Schema Refuses Results That Contradict Themselves

Types and field rules check one field at a time. Some mistakes are between fields: an `optimal`
result with no NPV, an `infeasible` one with a plan, a gap with no bound to measure it from. A
planner tool that receives one will show something false, and its developers cannot tell whether the
tool or the service is wrong. Pydantic's `@model_validator(mode="after")` runs after every field has
been checked, sees the whole object, and refuses it by raising `ValueError`:

```python
    @model_validator(mode="after")
    def consistent(self) -> "PlanResult":
        has_plan = self.npv is not None
        if self.status == "optimal" and not has_plan:
            raise ValueError("an optimal result must carry its plan's npv")
        if self.status in ("infeasible", "failed") and (has_plan or self.plan):
            raise ValueError(f"a result with status {self.status} has no plan")
        if (self.gap is None) != (self.npv is None or self.bound is None):
            raise ValueError("gap is given exactly when both npv and bound are")
        return self
```

The last rule is an equivalence: a gap is present if and only if both numbers it is computed from
are. A `time_limit` result may go either way (with a plan and a gap, or with neither), and the rules
allow both. `schema_rules.py` builds one consistent result, two odd ones, and five that break one rule each:

```python
broken = {
    "optimal, no npv": {**good, "npv": None, "gap": None},
    "infeasible with a plan": {**good, "status": "infeasible"},
    "gap below zero": {**good, "gap": -0.01},
    "gap but no bound": {**good, "bound": None},
    "status 'done'": {**good, "status": "done"},
}
```

```text
a consistent result      -> accepted: optimal
optimal, gap 0.06        -> accepted: optimal
no plan, a bound         -> accepted: time_limit
optimal, no npv          -> refused at the model: Value error, an optimal result must carry its plan's npv
infeasible with a plan   -> refused at the model: Value error, a result with status infeasible has no plan
gap below zero           -> refused at ['gap']: Input should be greater than or equal to 0
gap but no bound         -> refused at the model: Value error, gap is given exactly when both npv and bound are
status 'done'            -> refused at ['status']: Input should be 'optimal', 'time_limit', 'infeasible' or 'failed'
```

Field rules report the field (`['gap']`, `['status']`); the model validator reports the model as a
whole, with its message. The program also builds two odd results that pass: an `optimal` result
with a bound of 950 and a gap of 0.06, and a `time_limit` result with no plan but a bound of 1,000.
The validator checks only the three pairings in its code; it does not check that a proven plan's gap
is 0, or that the gap equals its formula. Those numbers come from `outcome_of`, and the module's
tests check them there. Because `fetch` returns a `PlanResult`, a bug in the worker that built such a
result would end in a server error inside the service, not in a wrong screen at the planner's desk.
That is the right place for it to fail.

The schema also documents itself. `PlanResult.model_json_schema()` is what FastAPI publishes in the
API's OpenAPI description (lesson 12.4.1), and every description written above is in it:

```text
fields a planner tool reads, from the JSON Schema:
  schema_version  string         changes only when a field changes meaning
  job_id          string         the id POST /jobs returned
  snapshot        string         sha256 of the request, the portfolio and the solver settings
  status          string         how the solve ended
  message         string         one paragraph for the planner, written from the fields below
  npv             number or null NPV of the plan, $k; null when there is no plan
  bound           number or null no plan is worth more than this, $k; null when unknown
  gap             number or null max(0, bound - npv) / max(|npv|, 1); null when there is no plan
  plan            array          one row per funded project; empty when there is no plan
  spend_by_year   array          one row per year; empty when there is no plan
```

`float | None` became "number or null": the schema tells the tool's developers which fields may be
empty before they find out from a crash.

<!-- practice 1 -->

## No Plan Means null, Never Infinity

A job that stops with no plan still has a bound: MathOpt's `best_objective_bound()` is always
available (its docstring says so), and with no plan in hand it can be infinite. `inf_and_null.py`
solves the large portfolio with a 1-second limit and follows that number into JSON:

```python
print("json.dumps               ->", json.dumps({"bound": bound}))
try:
    json.dumps({"bound": bound}, allow_nan=False)
except ValueError as error:
    print("json.dumps(allow_nan=False) ->", error)
```

```text
termination: NO_SOLUTION_FOUND | best_objective_bound(): inf
json.dumps               -> {"bound": Infinity}
json.dumps(allow_nan=False) -> Out of range float values are not JSON compliant: inf
```

The JSON standard has no infinity and no NaN. Python's `json.dumps` writes `Infinity` anyway, a
token many JSON parsers in other languages refuse, so the planner tool's code would fail on a reply
that Python produced without complaint. With `allow_nan=False`, Python refuses too. Pydantic chooses
a third way:

```python
class Loose(BaseModel):
    bound: float

sent = Loose(bound=bound).model_dump_json()
print("pydantic, bound: float   ->", sent)
try:
    Loose.model_validate_json(sent)
except ValidationError as error:
    print("  read back              ->", error.errors()[0]["msg"])
```

```text
pydantic, bound: float   -> {"bound":null}
  read back              -> Input should be a valid number
```

Pydantic wrote the infinite float as `null`, silently, and then refused to read its own output back,
because a `float` field does not accept null. A schema that says "number" sends null: the tool's
developers, reading the schema, would not expect it. The honest version declares the field
`float | None` and puts `None` there on purpose when the number does not exist:

```text
pydantic, float | None   -> {"bound":null} | read back: bound=None
```

That is what `PlanResult` does: `outcome_of` (lesson 12.4.2) sets `bound` only when it has a plan,
and `npv`, `bound` and `gap` are all `float | None`. The rule for every number in a result: if it
can be missing, say so in the type, and send `null`; never let an infinity or a NaN reach the JSON
writer.

<!-- practice 2 -->

## A Planner Tool Declares Only What It Reads, and the Service Only Adds Fields

The planner tool is another program, with its own release schedule. `planner_client.py` plays it: its
own pydantic models declare only the fields it reads (no `bound`, no `snapshot`, no `region`), and it
draws a summary from a result for the small portfolio with the 2029 budget cut to $7,000k:

```python
class PlannerView(BaseModel):          # the tool's model: no bound, no snapshot, no region
    status: str
    message: str
    npv: float | None
    gap: float | None
    plan: list[Row]
    spend_by_year: list[Year]
```

```text
[optimal] Best plan found and proven: NPV $23,645k.
year     spend  budget  headroom
2027     8,750   8,890       140
2028     7,970   8,120       150
2029     6,970   7,000        30
2030     8,610   8,610         0
2031     7,820   7,850        30
distribution   7 projects  $10,280k
transmission   9 projects  $26,720k
vegetation    10 projects  $3,120k
```

The cut cost $615k of NPV ($24,260k before), and the plan now spends 2030's budget to the last
thousand. The tool parsed the service's JSON with `model_validate_json` and drew every number from
it, without knowing about the fields it does not declare: pydantic's default for undeclared fields
is to ignore them. (The order of keys inside a JSON object carries no meaning either; pydantic reads
each field by name.) That default is what lets the service grow. The program then changes the
result in two ways:

```python
renamed = json.loads(body)
renamed["npv_k"] = renamed.pop("npv")         # the service renames a field the tool reads
try:
    PlannerView.model_validate(renamed)
except ValidationError as error:
    print("after renaming npv:", error.errors()[0]["loc"], error.errors()[0]["msg"])
added = {**json.loads(body), "region_spend": {"Valley": 1}}    # the service adds a field
print("after adding a field:", PlannerView.model_validate(added).status)
```

```text
after renaming npv: ('npv',) Field required
after adding a field: optimal
```

Adding a field broke nothing. Renaming one broke the tool at once, although the number was still
there under a new name. So the service follows one rule: **add fields, never rename, remove or
change the meaning of one** within a schema version. A change of that kind is a new
`schema_version`, served next to the old one until every tool has moved. The request side is the
opposite: lesson 12.4.1's `extra="forbid"` refuses unknown request fields, because a field the
service ignores there is a planner's setting that silently did nothing. Be strict in what the
service accepts and in what it promises, and let its readers ignore what they do not need.

## Summary

- **A result carries the plan, the money by year, the value, the gap, the status and a message,**
  as rows and typed fields with units, tied to its inputs by job id and snapshot.
- **Every field has one meaning, and the schema refuses results that contradict themselves.** Field
  rules check one field; a model validator checks the pairs (`optimal` needs `npv`; `infeasible` has
  no plan; a gap needs both numbers).
- **No plan means `null`, never infinity.** JSON has no infinity; `json.dumps` writes `Infinity`
  anyway, and pydantic writes `null` for a `float` it then cannot read back. Declare `float | None`.
- **A planner tool declares only what it reads, and the service only adds fields.** An added field
  was ignored; a renamed one failed with "Field required".

## Reference

| Field | Type | Meaning |
| --- | --- | --- |
| `schema_version` | `"1.0"` | changes only when a field changes meaning |
| `job_id`, `snapshot` | string | the job; sha256 of request, portfolio and settings |
| `status` | one of four | `optimal`, `time_limit`, `infeasible`, `failed` |
| `message` | string | for the planner, written from the fields |
| `npv`, `bound` | number or null ($k) | the plan's value; no plan is worth more than the bound |
| `gap` | number or null | $`\max(0,\ \text{bound} - \text{npv}) / \max(\lvert\text{npv}\rvert,\ 1)`$ |
| `plan` | list of rows | `project_id`, `start_year`, `program`, `region`, `capex`, `npv` |
| `spend_by_year` | list of rows | `year`, `spend`, `budget`, `headroom` |

| Pydantic | What it does |
| --- | --- |
| `Literal[...]` | a closed set of values; an `enum` in JSON Schema |
| `float \| None` | a number or null; "number or null" in JSON Schema |
| `@model_validator(mode="after")` | a rule between fields, run on the whole object |
| `model_dump_json()`, `model_validate_json()` | write and read JSON |
| `model_json_schema()` | the JSON Schema FastAPI publishes |
| default `extra="ignore"` | readers skip fields they do not declare |

**Further reading:** MathOpt's [`result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py)
(`best_objective_bound` is the dual bound and always available, even with no feasible solution;
`objective_value` raises when there is none); the OR-Tools
[MathOpt overview](https://developers.google.com/optimization/math_opt); pydantic,
[Models](https://pydantic.dev/docs/validation/latest/concepts/models/) (validation, `model_dump_json`,
`model_validate_json`, the `extra` setting and its `'ignore'` default),
[Fields](https://pydantic.dev/docs/validation/latest/concepts/fields/) (constraints and
`description`) and [JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema/)
(`model_json_schema`); FastAPI, [Response Model](https://fastapi.tiangolo.com/tutorial/response-model/)
(the return type validates, filters and documents the reply); lessons 7.1.3 (snapshot ids), 9.1.6
and 9.3.4.

## Challenges

1. Finance wants spend by region as well as by year. Add it without breaking `PlannerView`, and say
   which rule of the last section you followed.
2. A `time_limit` result with a plan has a gap of 0.004. Write the message a planner should read, and
   decide whether 0.4% belongs in the message or only in `gap`.
3. Should `npv` be a float or an integer number of $k? Look at the proven result's `npv` and at
   lesson 10.1.1, then decide.

## Design Note: One Schema, Several Readers

Lesson 9.3.4 writes three texts, for planners, finance and auditors, from one record. This lesson's
`PlanResult` is that record made public: each reader's screen is drawn from the same fields, and no
reader gets a number another does not. It would be tempting to add a field per screen
(`planner_summary`, `finance_table`) and let the service format each. Then a change in one screen
becomes a schema change for every tool. Keep the schema as data, with one short `message` for the
case where the planner needs words, and let each tool format the rest.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**result_json.py.** Fetches the result of a proven job and of an infeasible one through the job API
and prints their JSON (*A Result Carries the Plan*). *Try:* Submit `{"portfolio": "small",
"time_limit_s": 0.01}`. Predict the status and which fields are null.

**schema_rules.py.** Builds one consistent result and five broken ones, and prints the schema's
field descriptions (*Every Field Has One Meaning*). *Try:* Add a result with status `failed` and a
plan. Predict the message.

**inf_and_null.py.** Follows an infinite bound into `json.dumps` and into two pydantic models (*No
Plan Means null, Never Infinity*). *Try:* Use `float("nan")` instead of the bound. Predict each line.

**planner_client.py.** A planner tool's own model reads a result, draws a summary, then meets a
renamed and an added field (*A Planner Tool Declares Only What It Reads*). *Try:* Give `PlannerView`
`model_config = ConfigDict(extra="forbid")`. Predict the last line.

**schemas.py** is the result schema and `to_result`.

- Program: [result_json.py](src/result_json.py)
- Program: [schema_rules.py](src/schema_rules.py)
- Program: [inf_and_null.py](src/inf_and_null.py)
- Program: [planner_client.py](src/planner_client.py)
- Library: [schemas.py](src/schemas.py)
