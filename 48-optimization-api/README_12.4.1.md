# 12.4.1 A REST API with FastAPI

GridCap's planners do not run Python. They work in a planning tool, a web application with tables
of projects and budgets, and today, when they want a plan, they email an analyst, who changes a
budget in a script, runs it, and pastes the result back into a spreadsheet. The planning tool's
team asks for something they can call themselves: send a scenario, get a plan. This lesson builds
that: a small web API in front of the course's planning model, written with FastAPI and tested
without ever starting a server. (GridCap is the course's fictional utility; no number in it is real.)

A few words first. An **API** (application programming interface) is a set of requests one program
can send another. A **web API** receives them over HTTP, the protocol a browser uses: each request
names a **method** (`GET` to read, `POST` to send something to be processed) and a **path** such as
`/plans`, and may carry a **body**, here always JSON. Each reply carries a three-digit **status
code** (200 means it worked) and its own body. **REST** is the usual style for such APIs: paths name
things (a plan, a portfolio), and the method says what to do with them. **FastAPI** is a Python
library for writing web APIs. Its home page describes it as built on standard Python type hints,
with Starlette handling the web part and pydantic the data part. **Pydantic** (lesson 1.3.2) turns
a class with type hints into a validator that checks and converts incoming data.

## The Model

The API solves the multi-period model of lessons 6.4.1 and 6.4.2, unchanged except
that a request may replace any year's budget. This lesson adds no row; the marked parameter is the
one the request sets.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups, each
a set of projects; $`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$, the NPV of project $`i`$ started in year $`t`$ ($k);
$`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th year of work, $`k = 0, 1, \dots`$ ($k);
$`B_y`$, the budget of year $`y`$ ($k): the request's value for $`y`$ if it sends one, else the
portfolio's.

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
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \quad \leftarrow B_y \text{ from the request}
\end{aligned}
```

The row names in `plan_model.py` are the labels; on the tiny portfolio they include `must_P002`,
`once_P001`, `alt_G006`, `after_P004_2028` and `budget_2028`.

## An Endpoint Is a Path, a Method and a Function

In FastAPI, you create an application object and attach Python functions to it with decorators.
`@app.get("/health")` says: when a `GET` request for the path `/health` arrives, call the function
below and send back what it returns, converted to JSON. The FastAPI docs call such a function a
*path operation function*, and the pair of method and path an *endpoint*. Here are the planning
API's three endpoints, from `plan_api.py`:

```python
app = FastAPI(title="GridCap planning API", version="0.1.0")

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/portfolios/{name}", responses={404: {"description": "No portfolio has that name"}})
def portfolio_info(name: str) -> PortfolioInfo:
    if name not in ("tiny", "small"):
        raise HTTPException(status_code=404, detail=f"no portfolio named {name!r}")
    pf = generate(name)
    return PortfolioInfo(name=name, projects=len(pf.projects), years=list(pf.years), budget=dict(pf.budget))

@app.post("/plans")
def make_plan(request: PlanRequest) -> PlanResponse:
    pf = generate(request.portfolio)
    unknown = sorted(set(request.budget) - set(pf.years))
    if unknown:
        raise HTTPException(status_code=422, detail=f"budget years {unknown} are outside the plan's years {list(pf.years)}")
    pm = build(pf, {**pf.budget, **request.budget})
    params = mathopt.SolveParameters(time_limit=timedelta(seconds=request.time_limit_s))
    result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS, params=params)
    if not result.has_primal_feasible_solution():
        return PlanResponse(status=result.termination.reason.name.lower(), npv=None, starts={}, spend={})
    starts = starts_of(pm, result)
    return PlanResponse(status=result.termination.reason.name.lower(), npv=result.objective_value(),
                        starts=starts, spend=spend_of(pf, starts))
```

Three things FastAPI reads from these few lines:

- **`{name}` in a path is a path parameter.** FastAPI passes that part of the URL to the argument
  of the same name, so `GET /portfolios/tiny` calls `portfolio_info(name="tiny")`.
- **An argument typed as a pydantic model is the request body.** `make_plan(request: PlanRequest)`
  tells FastAPI to parse the JSON body, check it against `PlanRequest`, and pass the result in.
- **The return type is the response model.** `-> PlanResponse` makes FastAPI check what the
  function returns against `PlanResponse`, keep only its fields, and convert it to JSON. The docs
  note that a return value that does not fit becomes a server error, never a wrong reply.

`make_plan` is the whole optimization step: it builds the model with the request's budgets merged
over the portfolio's (`{**pf.budget, **request.budget}`: a later dict wins on a shared key), solves
it with HiGHS through MathOpt (lesson 4.2.1), and reads the plan with `starts_of` and the spend with
`spend_of`, both in `plan_model.py`.

### Calling it with no server

A web API normally runs inside a **server**, a program that listens on a network port and hands
each incoming request to the application. You do not need one to call the API. FastAPI's
`TestClient` (re-exported from Starlette, built on the HTTP library `httpx`) sends requests straight
into the application object, in the same process, and returns real HTTP responses. Everything in
this module runs that way, because the course's runner has no network. From `first_calls.py`:

```python
client = TestClient(app)

r = client.get("/health")
print("GET /health ->", r.status_code, r.json())
r = client.get("/portfolios/tiny")
print("GET /portfolios/tiny ->", r.status_code, r.json())

r = client.post("/plans", json={"portfolio": "tiny"})
print("POST /plans tiny ->", r.status_code)
print(json.dumps(r.json(), indent=1))
```

```text
GET /health -> 200 {'status': 'ok'}
GET /portfolios/tiny -> 200 {'name': 'tiny', 'projects': 8, 'years': [2027, 2028, 2029], 'budget': {'2027': 2300, '2028': 3280, '2029': 2310}}
POST /plans tiny -> 200
{
 "status": "optimal",
 "npv": 2473.0,
 "starts": {
  "P001": 2029,
  "P002": 2028,
  "P005": 2027,
  "P007": 2027,
  "P008": 2027
 },
 "spend": {
  "2027": 1120,
  "2028": 2730,
  "2029": 2150
 }
}
```

The tiny portfolio's plan funds five of its eight projects for an NPV of $2,473k, and spends less
than each year's budget. Look at the budget keys: `2027` was an `int` in Python and arrives as the
string `"2027"`. JSON allows only strings as object keys, so every `dict[int, ...]` loses its key
type on the way out. Lesson 12.4.3 returns spend as a list of rows for this reason.

`TestClient` also prints a warning on import in the runner: Starlette 1.10 announces that its test
client will move from `httpx` to a package named `httpx2`. It works the same either way. The
programs filter that one warning out, so their output shows only what they print.

To serve the same `app` to other machines, you would start a server. The FastAPI docs show
`fastapi dev` for development and `fastapi run` for production, both of which start Uvicorn, a
server program. This is read-along only: the course runs no server, and the runner image does not
include one.

```sh
# Not run in this course: it opens a network port, and the runner has no network.
fastapi run plan_api.py
```

The server would then answer the same requests at `http://<host>:8000/plans`. Lesson 12.5.1 packages
the service in a container for exactly that.

## The Request Is a Pydantic Model, and FastAPI Refuses What It Does Not Fit

The request a planner tool sends is a contract: which portfolio, which budgets to change, how long
the solver may run. `PlanRequest` writes that contract as a pydantic model:

```python
Money = Annotated[int, Field(ge=0, description="$k")]

class PlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    portfolio: Literal["tiny", "small"]
    budget: dict[int, Money] = Field(default_factory=dict, description="year -> budget; missing years keep the portfolio's")
    time_limit_s: float = Field(default=10.0, gt=0, le=60)
```

Each line is a rule:

- `Literal["tiny", "small"]` allows exactly those two strings. (The API solves inside the request,
  so it offers only the portfolios that solve in well under a second; lesson 12.4.2 lifts that.)
- `dict[int, Money]`: the keys must be whole numbers, and each value an `int` that is
  `ge=0` (greater than or equal to 0). `Field(...)` attaches such constraints, and `Annotated` lets
  one constrained type be reused.
- `default_factory=dict` gives each request its own empty dict when the field is left out.
- `gt=0, le=60`: the time limit is above 0 and at most 60 seconds.
- `extra="forbid"` refuses a field the model does not declare. Pydantic's default is to ignore
  one, which would let a misspelled `budgets` fall away silently and the job run on the default
  budgets.

When the body does not fit, FastAPI never calls `make_plan`. It answers **422 Unprocessable
Entity** with a list of errors, each giving the field's location (`loc`) and a message. From
`bad_requests.py`:

```python
for label, body in bad.items():
    r = client.post("/plans", json=body)
    error = r.json()["detail"][0]
    print(f"{label:<18} -> {r.status_code}  at {error['loc']}: {error['msg']}")
```

```text
negative budget    -> 422  at ['body', 'budget', '2028']: Input should be greater than or equal to 0
zero time limit    -> 422  at ['body', 'time_limit_s']: Input should be greater than 0
unknown portfolio  -> 422  at ['body', 'portfolio']: Input should be 'tiny' or 'small'
misspelled field   -> 422  at ['body', 'budgets']: Extra inputs are not permitted
year as text       -> 422  at ['body', 'budget', 'next year', '[key]']: Input should be a valid integer, unable to parse string as an integer
year outside plan  -> 422  budget years [2035] are outside the plan's years [2027, 2028, 2029]
GET unknown name   -> 404  no portfolio named 'huge'
```

The first five were refused by pydantic, each with the exact place the planner tool must fix. The
budget key `"2028"` arrived as a string and was accepted as the year 2028, because pydantic converts
a string that spells an integer; `"next year"` does not, so it was refused.

The last two came from the endpoints' own code. Whether 2035 is one of the plan's years depends on
the portfolio, which the request model does not know, so `make_plan` checks it and raises
`HTTPException(status_code=422, ...)`. FastAPI turns that exception into a reply with the given
code and `{"detail": ...}` as the body. `GET /portfolios/huge` gets **404 Not Found**: the path
names something that does not exist.

The order matters. Every check here runs before a model is built. A negative budget that reached
the model would not fail: it would produce a model with no plan, and the planner would read
"infeasible" when the truth is "you sent a typo".

<!-- practice 1 -->

## An Infeasible Scenario Is an Answer, Not an HTTP Error

Now a request that fits every rule but asks for the impossible. Must-do project P002 spends $2,730k
in 2028 (the plan above shows it), so a 2028 budget of $1,000k leaves the model no plan:

```python
r = client.post("/plans", json={"portfolio": "tiny", "budget": {"2028": 1000}})
print("POST /plans tiny, 2028 budget 1000 ->", r.status_code, r.json())
```

```text
POST /plans tiny, 2028 budget 1000 -> 200 {'status': 'infeasible', 'npv': None, 'starts': {}, 'spend': {}}
```

The reply is **200 OK** with `status: infeasible`. That is a choice, and the right one. An HTTP
status code says how the *exchange* went, not what the answer was. The request was well formed, the
server worked, and the optimizer answered the planner's question: no plan meets these budgets. That
answer goes in the body, where the planner tool reads it (lesson 9.1.1 separates infeasible from the
other ways a solve ends; lesson 12.4.2 gives each its own status). The codes this API uses:

| Code | Meaning here | Example |
| --- | --- | --- |
| 200 OK | the request was processed; read the body for the answer | a plan, or `status: infeasible` |
| 404 Not Found | the path names something that does not exist | `GET /portfolios/huge` |
| 422 Unprocessable Entity | the body does not fit the request's rules | a negative budget |
| 500 Internal Server Error | the server itself failed | a bug, or a solver crash |

If infeasible were a 4xx, the planner tool could not tell "you sent a broken request" from "your
scenario has no plan", and those need different actions: fix the request, or change the scenario.
If it were a 500, monitoring would page an engineer for a planner's budget cut.

<!-- practice 2 -->

## A Blocking Solve Belongs in a def Path, Never in async def

FastAPI accepts a path function written with `def` or with `async def`, and the two run differently.
The FastAPI docs on concurrency say a `def` path operation function is run in an external
threadpool, so it cannot block the server. An `async def` function runs directly on the server's
**event loop**, the single thread that switches between requests whenever one of them waits with
`await`. A solve never awaits: `mathopt.solve` holds its thread until it returns. Put it inside an
`async def`, and the event loop can do nothing else meanwhile.

`def_or_async.py` measures it. Each path blocks for one second with `time.sleep(1)`, standing in for
a solve, and three requests are sent at the same moment from three threads:

```python
@app.get("/async-solve")
async def async_solve() -> dict:
    time.sleep(1)           # blocks the event loop: nothing else runs meanwhile
    return {"done": True}

@app.get("/def-solve")
def def_solve() -> dict:
    time.sleep(1)           # FastAPI runs a def path in its threadpool, so the loop stays free
    return {"done": True}
```

```text
3 requests to /async-solve  took 3 s
3 requests to /def-solve    took 1 s
```

Under `async def`, the three requests ran one after another: the third planner waited three
seconds for a one-second answer, and a fourth request of any kind, even `GET /health`, would have
waited too. Under `def`, FastAPI ran each call in its own worker thread and all three finished
together. Every path in this module that solves is a `def`.

This is not yet a fix for long solves. A `def` path still holds its request open for as long as the
solve runs, and the threadpool has a fixed number of threads. A solve that takes minutes needs a
different shape, which is lesson 12.4.2.

## FastAPI Writes the API's Description From the Same Models

Every FastAPI application describes itself in **OpenAPI**, a standard format listing an API's paths,
methods, parameters and replies, with data shapes written in JSON Schema. A served app publishes it
at `/openapi.json` and draws interactive pages from it at `/docs`. The same description is available
in code from `app.openapi()`; `openapi_view.py` prints part of it:

```python
spec = app.openapi()
print("OpenAPI", spec["openapi"], "-", spec["info"]["title"], spec["info"]["version"])
for path, operations in spec["paths"].items():
    for method, op in operations.items():
        print(f"  {method.upper():<5} {path:<20} responses {sorted(op['responses'])}")
```

```text
OpenAPI 3.1.0 - GridCap planning API 0.1.0
  GET   /health              responses ['200']
  GET   /portfolios/{name}   responses ['200', '404', '422']
  POST  /plans               responses ['200', '422']
```

FastAPI added the 422 reply to every path that takes input, because it does the validation itself.
It did not discover the 404 that `portfolio_info` raises: that entry is there only because the
decorator declares it with `responses={404: ...}`. A reply the code raises but the decorator does
not declare is invisible to the planner tool's developers.

The request model's part of the description is pydantic's JSON Schema for `PlanRequest`
(`PlanRequest.model_json_schema()`), and each rule above appears in it:

```text
PlanRequest as JSON Schema:
{
 "additionalProperties": false,
 "properties": {
  "portfolio": {
   "enum": [
    "tiny",
    "small"
   ],
   "title": "Portfolio",
   "type": "string"
  },
  "budget": {
   "additionalProperties": {
    "description": "$k",
    "minimum": 0,
    "type": "integer"
   },
   "description": "year -> budget; missing years keep the portfolio's",
   "title": "Budget",
   "type": "object"
  },
  "time_limit_s": {
   "default": 10.0,
   "exclusiveMinimum": 0,
   "maximum": 60,
   "title": "Time Limit S",
   "type": "number"
  }
 },
 "required": [
  "portfolio"
 ],
 "title": "PlanRequest",
 "type": "object"
}
```

`extra="forbid"` became `"additionalProperties": false`, `ge=0` became `"minimum": 0`, `gt=0`
became `"exclusiveMinimum": 0`, and the `Literal` became an `enum`. Only `portfolio` is
`required`, because the other two fields have defaults. The rules are written once, in the model,
and the validation, the 422 messages and the published description all come from that one place.

## Summary

- **An endpoint is a path, a method and a function.** A decorator binds them; a path parameter, a
  pydantic body and a return type are read from the function's signature. `TestClient` calls the
  app with no server.
- **The request is a pydantic model, and FastAPI refuses what it does not fit.** A body that breaks
  a rule gets 422 with the field's location, before any model is built.
- **An infeasible scenario is an answer, not an HTTP error.** 200 with `status: infeasible`; 4xx
  only for a bad request, 5xx only for a broken server.
- **A blocking solve belongs in a `def` path, never in `async def`.** Three one-second calls took
  3 s under `async def` and 1 s under `def`.
- **FastAPI writes the API's description from the same models.** OpenAPI and JSON Schema come from
  the models and decorators; declare every reply you raise.

## Reference

| FastAPI or pydantic | What it does |
| --- | --- |
| `@app.get(path)`, `@app.post(path)` | bind a function to a method and a path |
| `{name}` in a path | a path parameter, passed to the argument `name` |
| argument typed as a `BaseModel` | the JSON body, validated |
| `-> Model` | the response model: validated, filtered, converted to JSON |
| `HTTPException(status_code, detail)` | stop and answer that code with `{"detail": ...}` |
| `responses={404: {...}}` | declare a reply in the OpenAPI description |
| `Field(ge=, gt=, le=, default_factory=)` | rules and defaults on a field |
| `ConfigDict(extra="forbid")` | refuse undeclared fields (default: ignore them) |
| `TestClient(app).post(path, json=...)` | call the app in-process |
| `app.openapi()`, `Model.model_json_schema()` | the API's description, a model's schema |

| Term | Meaning |
| --- | --- |
| endpoint | one method and path, and the function behind it |
| status code | three digits on each reply: 2xx worked, 4xx the client's fault, 5xx the server's |
| event loop | the thread that runs `async def` code, switching at each `await` |
| threadpool | the worker threads in which FastAPI runs `def` path functions |
| OpenAPI | a standard description of an API, its data shapes in JSON Schema |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt)
(modeling kept separate from solving, the property that lets an endpoint build a model from a
request and hand it to any solver); the OR-Tools MathOpt sample
[`integer_programming.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py)
(it checks the termination reason before reading values, as `make_plan` does); FastAPI,
[home page](https://fastapi.tiangolo.com/), [First Steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
(paths, operations, `fastapi dev` and `fastapi run`, `/docs` and `/openapi.json`),
[Response Model](https://fastapi.tiangolo.com/tutorial/response-model/),
[Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) (`HTTPException` and the
default 422 body), [Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/),
[Concurrency and async / await](https://fastapi.tiangolo.com/async/) (`def` paths in a threadpool)
and [Testing](https://fastapi.tiangolo.com/tutorial/testing/) (`TestClient`); pydantic,
[Models](https://pydantic.dev/docs/validation/latest/concepts/models/) (`extra="forbid"`),
[Fields](https://pydantic.dev/docs/validation/latest/concepts/fields/) and
[JSON Schema](https://pydantic.dev/docs/validation/latest/concepts/json_schema/).

## Challenges

1. Add `GET /plans/latest`, which returns the last plan the API computed. What goes wrong when two
   planners use the API at once?
2. A planner sends the same budget for 2028 twice in one JSON object. What does Python's JSON parser
   keep, and should the API refuse such a body?
3. `make_plan` uses a 10-second default time limit. Which status would a planner see if a small
   solve hit it, and is a 200 still right?

## Design Note: Validate at the Edge, Model in the Middle

The checks in this lesson sit at the edge of the service: the request model and the first lines of
an endpoint. The model builder (`plan_model.build`) checks nothing and trusts its input. You could
put the checks in the builder instead, so that every caller, not only the API, benefits. Lessons 12.2.1
and 12.2.2 do part of that for the data itself. The split here is by audience: the edge
refuses what a caller can fix and names the field; the builder assumes a valid scenario and states
the model. A check in both places is fine; a check in neither is how a typo becomes "infeasible".

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**first_calls.py.** Calls the health, portfolio and plan endpoints through `TestClient`, then asks
for a 2028 budget too small for the must-do projects (*An Endpoint Is a Path, a Method and a
Function* and *An Infeasible Scenario Is an Answer*). *Try:* Send a 2028 budget of $2,730k, exactly
P002's spend that year. Predict the status before running.

**bad_requests.py.** Sends six requests that break a rule and one unknown portfolio name, and prints
each reply's code and error (*The Request Is a Pydantic Model*). *Try:* Send `"time_limit_s": "5"`
(a string). Predict whether pydantic accepts it.

**def_or_async.py.** Times three simultaneous calls to a blocking path declared `async def`, then
`def` (*A Blocking Solve Belongs in a def Path*). *Try:* Send six calls instead of three. Predict
both times.

**openapi_view.py.** Prints the API's OpenAPI paths and `PlanRequest`'s JSON Schema (*FastAPI
Writes the API's Description*). *Try:* Remove `responses=...` from `portfolio_info`'s decorator.
Predict which line of the output changes.

**plan_api.py** is the API itself, and **plan_model.py** the model it solves.

- Program: [first_calls.py](src/first_calls.py)
- Program: [bad_requests.py](src/bad_requests.py)
- Program: [def_or_async.py](src/def_or_async.py)
- Program: [openapi_view.py](src/openapi_view.py)
- Library: [plan_api.py](src/plan_api.py)
- Library: [plan_model.py](src/plan_model.py)
