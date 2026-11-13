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
