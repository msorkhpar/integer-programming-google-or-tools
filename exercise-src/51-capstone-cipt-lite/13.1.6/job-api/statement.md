A planning run takes minutes, and the service restarts whenever it is redeployed. Planners must be
able to submit a run, close the browser, and fetch the plan after lunch, even if the service was
restarted in between. Your milestone is the job API, with each job's state and result kept in a
local SQLite file. The solves are stand-ins in the tests; the portfolio behind them is invented for
a fictional utility.

`create_app(solve, db_path)` returns the FastAPI app. `solve(budget)` is the planning run: it takes
`{year: $k}` budget overrides, with integer years, and returns a JSON-ready dict with a `"status"`
of `"optimal"` or `"infeasible"`; it may also raise. The request model `PlanRequest` (only a
`budget` field, extra fields refused) is given.

| endpoint | contract | lesson |
| --- | --- | --- |
| `POST /jobs` | add a row for the job in state `queued`, hand the solve to a one-thread `ThreadPoolExecutor`, and answer 202 at once with `{"job_id": <id>, "poll": "/jobs/<id>", "result": "/jobs/<id>/result"}` and a `Location: /jobs/<id>` header | 12.4.2 |
| `GET /jobs/{id}` | `{"job_id", "state", "finished"}`; the state is `queued`, `running`, `optimal`, `infeasible` or `failed`; 404, with the id in its `detail`, for an id the service never gave out | 12.4.2 |
| `GET /jobs/{id}/result` | 404 for an unknown id, 409 while the job has not finished, otherwise the result the solve returned (for a failed job, `{"status": "failed", "error": "<type>: <message>"}`) | 12.4.2, 12.4.3 |

Keep the jobs in a table of the SQLite file at `db_path`: `CREATE TABLE IF NOT EXISTS job (id TEXT
PRIMARY KEY, request TEXT NOT NULL, state TEXT NOT NULL, result TEXT) STRICT`, with the result as
JSON text. Open the connection with `check_same_thread=False` (the worker thread writes to it) and
guard it with a lock. The worker sets `running`, calls the solve, and writes the final state and
result; an exception from the solve fails that job only. Lesson 12.1.4 covers SQLite, and lessons
12.4.1 to 12.4.3 the API. About forty-five lines.
