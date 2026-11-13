The planner is trusted now, and the vegetation program asked for one more thing:

> We don't want to run a Python script on someone's laptop. Give us an endpoint: we POST a season
> (the same JSON our inventory exports) and the planner's overrides, and get back the plan's record.
> Keep every plan you return, so we can fetch it again by its id months later, after the laptop is
> gone. Bad input should be refused with a reason, before anything runs.

You start from the planner with records. Put an HTTP service in front of the library: a POST of a
season and its overrides answers with the plan's record and an id, and a GET of that id answers the
same body later, from a new service on the same SQLite file too. Refuse a season that breaks the
schema, or an override that names nothing, with 422 and the reason, before any model is built. A
season with no plan is an answer, with its explanation. An unknown id is 404.

**`main.py`.** After the record line, print an empty line and three lines from the service, called
in-process through FastAPI's `TestClient` on `create_app(":memory:")` (import `TestClient` inside
`warnings.catch_warnings()` with `warnings.simplefilter("ignore")`, since importing it prints a
deprecation notice about httpx). POST `{"season": <the tiny season's dict, seed 54>}` to `/plans`
and print `POST /plans -> <status code>, id <id>, <record status>, risk carried $<risk carried>k`;
GET `/plans/<id>` and print `GET /plans/<id> -> <status code>, same body: <True or False>`, comparing
the two JSON bodies; then print `GET /plans/7 -> <status code>`.

Run's report gains that section, as `expected/report.txt` shows. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.

### Blueprint

Write each method below. The tests check each one by itself and the whole program end to end, so you may change any other part of the code as you see fit.

#### `create_app` in `vegcrew/api.py`

```python
def create_app(db: str = ":memory:") -> FastAPI
```

- **Contract.** Returns a FastAPI app whose plans are kept in a Store on the SQLite file db. store.py is new: Store(path) opens one connection (check_same_thread=False, shared under a threading.Lock) and creates the table plans (id INTEGER PRIMARY KEY, input_sha256 TEXT, record TEXT), the record stored as dumps writes it; save(record) -> int inserts a row and returns its id; get(plan_id) -> dict | None returns the stored record parsed back with json.loads, or None for an id with no row. The request is checked by pydantic models in api.py: Span = tuple[int, int]; CircuitIn with id and region (str), miles (int, > 0), cost and risk (int, >= 0), weeks (int, >= 1), growth (float, >= 0), windows (list[Span], default []) and must (bool, default False); SeasonIn with name (default 'season'), budget (int, >= 0), crews (int, 1 to 50), months (int, 1 to 12), crew_off (dict[str, list[Span]], default {}) and circuits (list[CircuitIn], at least one); OverrideIn with kind (pin, skip or force), cid, crew (default None), start (default None) and reason (default ''); PlanRequest with season (SeasonIn) and overrides (list[OverrideIn], default []). POST /plans takes a PlanRequest; it answers 422 with the list of problems when check_overrides finds any, else plans the season (from the validated season's model_dump()) and answers {'id', 'record'}, an infeasible season included. GET /plans/`<id>` answers the same body, or 404 with `no plan <id>`.
- **Modeling idea.** Validate at the edge, keep the service a thin layer over the library, and store every answer so it outlives the process.
- **Taught in** [12.4.1 A REST API with FastAPI](../../../../12-engineering-the-optimization-service/48-optimization-api/units/unit-01/12.4.1-a-rest-api-with-fastapi.unit.html).
