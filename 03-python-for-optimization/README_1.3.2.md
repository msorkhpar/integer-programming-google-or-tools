# 1.3.2 Typed Inputs with Dataclasses and Pydantic

The pandas check of lesson 1.3.1 catches GridCap's six bad rows, and then hands the model a
DataFrame row: a bag of columns whose types depend on the file. The model code downstream still
reads `row["must_do"]` and hopes it is a boolean. A second team now wants to send projects from a
web form as plain dicts of strings, which never pass through pandas at all. This lesson gives a
project a type of its own, checked once where the data comes in, in three rules. GridCap is a
fictional utility, and its files are generated, not real data.

## A Dataclass Names Each Field's Type but Never Checks It

A **dataclass** is a class whose fields are declared with type annotations; Python writes its
constructor, its `==` and its printed form. `frozen=True` forbids changing a field after the object
is built. Here is one built from a row of `projects.csv`, read with the standard `csv` module, which
gives every cell as a string:

```python
@dataclass(frozen=True)
class ProjectRecord:
    project_id: str
    cost_profile: tuple[int, ...]
    must_do: bool
```

```python
def record(row: dict[str, str]) -> ProjectRecord:
    return ProjectRecord(row["project_id"], row["cost_profile"], row["must_do"])
```

```text
ProjectRecord(project_id='P003', cost_profile='980;1490', must_do='0')
type of cost_profile: str
P003 lasts 8 years
P001 is must-do: True
sum(cost_profile) fails: unsupported operand type(s) for +: 'int' and 'str'
assigning a field fails: cannot assign to field 'must_do'
```

The annotation says `tuple[int, ...]`, and the field holds the string `'980;1490'`. Python does not
check annotations at run time; they are documentation for people and for tools like type checkers.
So the record is wrong in two quiet ways and one loud one. `len()` of the string counts characters,
so the two-year project "lasts 8 years". `must_do` is the string `'0'`, and every non-empty string is
true, so P001 becomes a compliance project. Only `sum()` fails, because adding an int to a string is
an error.

The quiet failures are the dangerous ones: a model built from these records would force P001 into
every plan and stretch P003's spending over eight years, and nothing would crash. `frozen=True` does
its part (the last line): once a record exists, nobody can change it by accident. What a dataclass
cannot do is make sure the record was right when it was built.

## Pydantic Converts Each Field at the Boundary, or Says Why It Cannot

[Pydantic](https://docs.pydantic.dev/) checks types at run time. A class that inherits from
`BaseModel` declares its fields like a dataclass, and building one **validates** the input: each
value is converted to its field's type, or the build fails with a `ValidationError` that lists every
problem. This is the **boundary**: the one place data from outside (a file, a form, an API) becomes
objects the rest of the program trusts.

What does "converted" mean for a string? `TypeAdapter(int)` applies one field's conversion on its own:

```text
int  '2150'    -> 2150
int  ' 2150 '  -> 2150
int  '2150.0'  -> 2150
int  '2150.5'  -> rejected: Input should be a valid integer, unable to parse string as an integer
int  '2,150'   -> rejected: Input should be a valid integer, unable to parse string as an integer
bool '0'       -> False
bool '1'       -> True
bool 'yes'     -> True
bool '2'       -> rejected: Input should be a valid boolean, unable to interpret input
```

This is pydantic's default **lax** mode: a string that clearly means a number or a yes/no is
converted, and anything that would need a guess is rejected. `'2150.5'` would lose its half and
`'2,150'` could be a thousands separator or a decimal comma, so both are refused, which is the
"reject, don't repair" rule of lesson 1.3.1 built in. If even `'2150'` should be refused (an API that
promises real numbers), `ConfigDict(strict=True)` turns conversion off:

```text
strict int '2150' -> rejected: Input should be a valid integer
```

Here is a whole row of `projects.csv` as a model:

```python
class ProjectRow(BaseModel):
    model_config = ConfigDict(frozen=True)

    project_id: str
    program: Program
    region: Region
    cost_profile: tuple[NonNegativeInt, ...]
    earliest_start: int
    latest_start: int
    must_do: bool
    parent: str | None
    alt_group: str | None

    @field_validator("cost_profile", mode="before")
    @classmethod
    def split_years(cls, value):
        return value.split(";") if isinstance(value, str) else value

    @field_validator("parent", "alt_group", mode="before")
    @classmethod
    def blank_is_none(cls, value):
        return value or None
```

Each annotation is now a rule. `str | None` means "a string or `None`". `Program` and `Region` are
`Literal[...]` types (defined at the top of the program, with the three program and four region
names), so only the listed
names pass. `NonNegativeInt` is an `int` that must be 0 or more, so a negative cost fails. A
**field validator** is a method pydantic runs for one field; with `mode="before"` it runs on the raw
input, before the type conversion. Pydantic asks for field validators to be class methods
(`@classmethod`, receiving the class as `cls`), because they run before any object exists.
`split_years` turns `'980;1490'` into two strings for the `int` conversion to handle, and `blank_is_none` turns the CSV's empty cell into `None`, so "no parent" has
one spelling. Columns the class does not declare, such as `name` and `crew_months`, are ignored.

`ProjectRow.model_validate(row)` builds a `ProjectRow` from a dict such as a `csv.DictReader` row, or
raises `ValidationError`. Here it is on the rows of P003 and P001 that fooled the dataclass:

```text
project_id='P003' program='transmission' region='Coast' cost_profile=(980, 1490) earliest_start=2027 latest_start=2027 must_do=False parent=None alt_group=None
P003 lasts 2 years and costs 2470
P001 is must-do: False
```

The same two rows that fooled the dataclass now come out right: P003 lasts two years and P001 is
not must-do.

A bound that has no ready-made type, such as "above 0", goes on the field with `Field(...)`: write
the type, then `= Field(gt=0)` ("greater than 0"; `ge`, `lt` and `le` are "at least", "below" and
"at most"). `portfolio.json` holds the discount rate, which must be above 0, and the capital budget:

```python
class PlanSettings(BaseModel):
    """The two numbers of portfolio.json the models use."""
    discount_rate: float = Field(gt=0)
    capital_budget: NonNegativeInt
```

```python
print(PlanSettings.model_validate(settings))
for rate in ("0", "", "0.07"):
    try:
        print(f"discount_rate {rate!r:6} ->", PlanSettings.model_validate({**settings, "discount_rate": rate}))
    except ValidationError as error:
        print(f"discount_rate {rate!r:6} -> rejected:", error.errors()[0]["msg"])
```

```text
discount_rate=0.07 capital_budget=7390
discount_rate '0'    -> rejected: Input should be greater than 0
discount_rate ''     -> rejected: Input should be a valid number, unable to parse string as a number
discount_rate '0.07' -> discount_rate=0.07 capital_budget=7390
```

`settings` is the dict read from `portfolio.json`; its other keys (`name`, `seed`, `years`) are
ignored. `{**settings, "discount_rate": rate}` is a copy of it with one value replaced. A rate of
`'0'` breaks `gt=0`, and a blank cell `''` is not a number at all, so a `float` field rejects it
rather than reading it as 0.

What does pydantic say about a failure? `ValidationError.errors()` returns a list with one dict per
problem. Here is the first entry for P010 (cost `-400`) and for the rate `'0'`:

```python
for row in (rows[9], {**settings, "discount_rate": "0"}):
    model = ProjectRow if "project_id" in row else PlanSettings
    try:
        model.model_validate(row)
    except ValidationError as error:
        entry = error.errors()[0]                # one dict per problem
        print({key: entry[key] for key in ("type", "loc", "msg", "input")})
```

```text
{'type': 'greater_than_equal', 'loc': ('cost_profile', 0), 'msg': 'Input should be greater than or equal to 0', 'input': '-400'}
{'type': 'greater_than', 'loc': ('discount_rate',), 'msg': 'Input should be greater than 0', 'input': '0'}
```

`loc` (location) is a tuple whose first item is always the field's name: `('discount_rate',)`. When
the problem is inside a field, more items follow: `('cost_profile', 0)` is item 0 of the cost
profile, the first year. `msg` is the message, and `input` the value that failed. The entry also
has keys this program leaves out (`ctx`, `url`).

<!-- practice 1 -->

## A Rule Across Fields Goes in a Model Validator; a Rule Across Rows Goes Over the Whole File

Some rules need two fields at once: a project's window is empty if its earliest start is after its
latest. A **model validator** with `mode="after"` runs once every field has been converted, and sees
the whole object:

```python
@model_validator(mode="after")
def window_is_ordered(self):
    if self.earliest_start > self.latest_start:
        raise ValueError("earliest start after latest")
    return self
```

Now the six rows the planner appended in lesson 1.3.1, each validated alone:

```text
P009 rejected: cost_profile.0: Input should be a valid integer, unable to parse string as an integer
P010 rejected: cost_profile.0: Input should be greater than or equal to 0
P011 rejected: row: Value error, earliest start after latest
P012 rejected: region: Input should be 'Ridge', 'Valley', 'Coast' or 'Plains'
P008 accepted
P013 accepted
```

Each error names where it is: `cost_profile.0` is the first year of the profile (the `loc`
`('cost_profile', 0)` above, joined with a dot by the helper `reasons` shown in the next code), and
`row` marks the model validator, which belongs to no single field. Two rows pass, and they should, as single rows:
the second P008 is a perfectly good project on its own, and P013's parent P099 is a well-formed id.
"Ids are unique" and "a parent exists" are rules about the whole file, and no single row can break
them alone. They go in the code that sees every row:

```python
def load(rows: list[dict[str, str]]) -> tuple[list[ProjectRow], list[tuple[int, str, str]]]:
    """The rows that pass every rule, and (file line, project id, reason) for each that does not."""
    parsed, rejected = [], []
    for line, row in enumerate(rows, start=2):
        try:
            parsed.append((line, ProjectRow.model_validate(row)))
        except ValidationError as error:
            rejected += [(line, row["project_id"], reason) for reason in reasons(error)]

    copies = Counter(p.project_id for _, p in parsed)
    rejected += [(line, p.project_id, "duplicate id") for line, p in parsed if copies[p.project_id] > 1]
    kept = [(line, p) for line, p in parsed if copies[p.project_id] == 1]
    known = {p.project_id for _, p in kept}
    rejected += [(line, p.project_id, "unknown parent") for line, p in kept if p.parent and p.parent not in known]
    kept = [(line, p) for line, p in kept if not p.parent or p.parent in known]
    return [p for _, p in kept], sorted(rejected)
```

`enumerate(rows, start=2)` numbers the rows from 2, so each number is the row's line in the file (the
header is line 1). `Counter` (from `collections`) counts how often each id occurs among the rows that
passed. `load` catches each row's `ValidationError` and keeps going, so one bad row does not hide the next.
Then it runs the rules across rows, in order: duplicates first, then parents, checked against the
projects that survived, because a parent that was itself rejected is no parent the model can use.
`reasons(error)` is a short helper, defined in `pydantic_rows.py`, that turns pydantic's list of
errors into `field: message` strings:

```python
def reasons(error: ValidationError) -> list[str]:
    """Each problem pydantic found, as `field: message` (a whole-row rule has no field)."""
    return [f"{'.'.join(str(part) for part in e['loc']) or 'row'}: {e['msg']}" for e in error.errors()]
```

It joins each `loc` with dots, so `('cost_profile', 0)` becomes `cost_profile.0`. An error raised
by a model validator belongs to no field, and its `loc` is the empty tuple `()`; joining that gives
the empty string, and `or 'row'` puts the label `row` in its place. That is where `row:` in the
output above comes from.

```text
line  9  P008  duplicate id
line 10  P009  cost_profile.0: Input should be a valid integer, unable to parse string as an integer
line 11  P010  cost_profile.0: Input should be greater than or equal to 0
line 12  P011  row: Value error, earliest start after latest
line 13  P012  region: Input should be 'Ridge', 'Valley', 'Coast' or 'Plains'
line 14  P008  duplicate id
line 15  P013  unknown parent

14 rows read, 7 rejected, 7 kept: P001 P002 P003 P004 P005 P006 P007
same lines as the pandas check of lesson 1.3.1: True
```

The pydantic loader rejects exactly the lines the pandas masks did, and the last line of output
checks that. The difference is what comes out: a list of frozen `ProjectRow` objects whose every
field has the type it claims, which model code can use without checking again.

<!-- practice 2 -->

## The Model

The selection model of lesson 1.1.1, unchanged. What changes in this lesson is what the loader
promises about its data before the model is built.

**Sets.** $`P`$ the candidate projects; $`M \subseteq P`$ the must-do projects; $`C \subseteq P`$
the child projects, each with parent $`p(c) \in P`$; $`\mathcal{G}`$ the alternative groups, each a
set of projects.

**Parameters.** $`\text{capex}_i`$, the sum of project $`i`$'s cost profile ($k);
$`\text{npv}_i`$, its NPV if it starts in its earliest start year ($k); $`B`$, the capital budget
($k).

**Variables.** $`x_i \in \{0, 1\}`$ for each $`i \in P`$: 1 if project $`i`$ is funded.

**Objective.**

```math
\max \; \sum_{i \in P} \text{npv}_i\, x_i
```

**Constraints.**

```math
\begin{aligned}
\sum_{i \in P} \text{capex}_i\, x_i &\le B && && \text{(budget)} \\
x_i &= 1 && \forall i \in M && \text{(must}_i) \\
x_c &\le x_{p(c)} && \forall c \in C && \text{(parent}_c) \\
\sum_{i \in g} x_i &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

| The model assumes | Checked by |
| --- | --- |
| each project in $`P`$ once, so one variable per project | `load`: duplicate id |
| $`\text{capex}_i`$ is a sum of whole $k amounts, none negative | `ProjectRow.cost_profile`: `tuple[NonNegativeInt, ...]` |
| $`i \in M`$ only for a real yes | `ProjectRow.must_do`: `bool` |
| $`p(c) \in P`$ for every child | `load`: unknown parent |
| a start window $`e_i \le l_i`$ that holds a year (later models choose a start in it) | `window_is_ordered` |
| a region with a budget (regional spend rules come in lesson 6.5.5) | `ProjectRow.region`: `Region` |

## Summary

- **A dataclass names each field's type but never checks it.** Built from strings, it holds strings,
  and the wrong answers it gives are quiet ones.
- **Pydantic converts each field at the boundary, or says why it cannot.** Lax mode converts what is
  unambiguous and rejects what needs a guess; field validators prepare raw values first.
- **A rule across fields goes in a model validator; a rule across rows goes over the whole file.**
  Validate each row, collect every error, then check uniqueness and references over the survivors.

## Reference

| Need | Pydantic |
| --- | --- |
| A checked record | `class Row(BaseModel): field: type` |
| Build one from a dict | `Row.model_validate(data)` |
| No changes after building | `model_config = ConfigDict(frozen=True)` |
| No conversion from strings | `ConfigDict(strict=True)` |
| One of a few names | `Literal["a", "b"]` |
| Number bounds | `NonNegativeInt`, or on a field: `rate: float = Field(gt=0)` (also `ge`, `lt`, `le`) |
| Prepare a raw value | `@field_validator("f", mode="before")` |
| A rule over several fields | `@model_validator(mode="after")` |
| Every problem found | `except ValidationError as e: e.errors()`: one dict per problem, with `loc` (field name first, then positions inside it; `()` for a model validator), `msg` and `input` |
| One type on its own | `TypeAdapter(int).validate_python(value)` |

**Further reading:** [Python `dataclasses`](https://docs.python.org/3/library/dataclasses.html) (the decorator reads annotations only to find the fields and never checks their types; `frozen=True` raises `FrozenInstanceError`); [Pydantic: conversion table](https://pydantic.dev/docs/validation/latest/concepts/conversion_table/) (which inputs each type accepts in lax and in strict mode, including the strings a `bool` reads as true and false); [Pydantic: validators](https://pydantic.dev/docs/validation/latest/concepts/validators/) (before, after, plain and wrap field validators, and model validators that return the validated object).

## Challenges

1. A web form sends `"must_do": "no"`. Does `ProjectRow` accept it, and as what? Check your answer
   against the conversion table above before you run it.
2. P004's parent P003 is fine. If P003 were rejected for a bad cost, `load` would reject P004 too.
   What happens to a child of P004, two levels down?
3. Should `load` reject a project whose `alt_group` has only one member? What would that row do to the
   (alt) constraint?

## Design Note: Validate Once, at the Edge

Every function that receives a project could check it again, and some codebases do. The checks then
drift apart, and none of them knows which file line to blame. This course validates once, where data
enters (`load`), and passes frozen, typed objects inward. Model code can then read `p.must_do` as a
boolean without a second thought, because the type promises it and nothing can change it on the way.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**dataclass_trust.py.** Builds dataclass records from CSV strings and shows what they get wrong
(*A Dataclass Names Each Field's Type but Never Checks It*). *Try:* Add `parent: str | None` to
`ProjectRecord` and fill it from the row. Predict what P001's parent is.

- Program: [dataclass_trust.py](src/dataclass_trust.py)

**pydantic_rows.py.** Shows lax conversion, defines `ProjectRow` and `PlanSettings`, prints two
`errors()` entries, and validates the appended rows one at a time (*Pydantic Converts Each Field at
the Boundary*). *Try:* Add `strict=True` to
`model_config`. Predict how many of the tiny portfolio's rows still validate.

- Program: [pydantic_rows.py](src/pydantic_rows.py)

**load_portfolio.py.** Loads the dirty export: row rules through `ProjectRow`, then duplicates and
parents across rows (*A Rule Across Fields Goes in a Model Validator*). *Try:* Move the parent check
before the duplicate check. Does any line of the report change?

- Program: [load_portfolio.py](src/load_portfolio.py)
