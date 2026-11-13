# 13.1.6 Service: FastAPI Job API, Moto-Tested S3 Store, Pareto Frontier Endpoint

The planners' tool, finance's spreadsheet and the asset team's dashboard all want CIPT Lite, and
none of them will run Python scripts. The last milestone puts the five before it behind an HTTP
API: a client posts a snapshot and gets its digest, posts a job and gets an id at once, polls it,
and fetches a result that names its snapshot; it can also ask for the NPV-risk frontier, so the
board's choice of weights in lesson 13.1.3 is made with the trade-off in view. Snapshots and
results live in S3, job states in a local SQLite file, and every test runs offline: S3 is moto's
in-memory fake, reached with moto's fake credentials, and the API is called through FastAPI's
`TestClient`. GridCap is a fictional utility's portfolio.

## The Model

The frontier endpoint solves the model of the lesson *Model: Multi-Period Selection With All
Section 6 Rules*, unchanged (sets, parameters, $`x_{i,t} \in \{0, 1\}`$, and the rows once, must,
force, alt, after, budget, region, crews and floor, written out there), with the risk coefficients
$`\text{rr}_{i,t}`$ of the lesson *Value: NPV by Start Year, Risk Reduction From PoF/RUL, Weighted
Value* and **one row added**, the ε-constraint of lesson 8.3.1:

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
\quad \text{subject to every row of that model and} \quad
\sum_{i \in P} \sum_{t \in T_i} \text{rr}_{i,t}\, x_{i,t} \ge \varepsilon \qquad \text{(floor)}
```

solved once for each floor $`\varepsilon`$ between the risk removed by the NPV plan and the most
risk any plan removes (the payoff table, lesson 8.3.1).

## Snapshots and Results Live in S3, Job States in a Local SQLite File

Where each piece of state lives follows from how it is used. A snapshot is written once and read by
every job that solves it, so it goes to S3 under its digest, as the store of lesson 13.1.1 did on
disk (lesson 12.2.3):

```python
    def put_snapshot(self, pf: Portfolio) -> str:
        data = canonical(pf)
        key = hashlib.sha256(data).hexdigest()
        if not self.exists(f"snapshots/{key}.json"):
            self.s3.put_object(Bucket=self.bucket, Key=f"snapshots/{key}.json", Body=data,
                               ContentType="application/json")
        return key
```

`exists` asks S3 for the object's metadata with `head_object`, which returns no body and raises a
`ClientError` with code 404 when the key is absent. S3 itself would accept a second `put_object` to
the same key and replace the object; the `exists` check is what makes a repeated post store nothing. Reading re-hashes the bytes and refuses an
object that no longer matches its name:

```python
    def get_snapshot(self, digest: str) -> Portfolio:
        data = self.s3.get_object(Bucket=self.bucket, Key=f"snapshots/{digest}.json")["Body"].read()
        if hashlib.sha256(data).hexdigest() != digest:
            raise Corrupted(f"snapshots/{digest[:12]}.json no longer hashes to its name")
        return Portfolio.from_dict(json.loads(data))
```

A job's result is written once, when the job ends, so it goes to S3 too, under `results/<job
id>.json`. A job's **state** (queued, running, optimal, infeasible...) changes several times and is
read on every poll, so it goes to a table in a local SQLite file, one row per job, declared
`STRICT` so that a wrong type is refused rather than stored (lesson 12.1.4). That is the split of
lesson 12.5.3, and the course uses no cloud database.

`service_demo.py` runs the whole service with no network. Before it imports boto3, it sets moto's
fake credentials (`AWS_ACCESS_KEY_ID=testing` and the rest), so that no real account can ever be
reached; inside `with mock_aws():`, every S3 call goes to moto's in-memory S3 (lesson 12.5.4). Posting GridCap medium twice, and a copy with a parent cycle:

```text
POST /snapshots  -> 201, snapshot df4edafe8608
posted again     -> same snapshot True; objects in S3: 1
a parent cycle   -> 422, ['parent-cycle: P050 -> P051 -> P050']
```

The digest is lesson 13.1.1's, the second post stores nothing new, and a snapshot the quality gate
refuses never reaches S3: the endpoint runs `gate` and answers 422 with the findings.

<!-- practice 1 -->

## A Job Is Accepted at Once, Polled, Then Fetched

A medium solve takes many seconds, and an HTTP request must not wait for it (lesson 12.4.2). Submit
checks the request, writes the job's row, hands the solve to an executor and answers **202
Accepted** with the job's id and a `Location` header:

```python
    @app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
    def submit(request: JobRequest, response: Response) -> dict:
        pf = snapshot_of(request.snapshot)
        unknown = sorted(set(request.budget) - set(pf.years))
        if unknown:
            raise HTTPException(status_code=422, detail=f"years outside the plan: {unknown}")
        job_id = uuid.uuid4().hex[:12]
        table.add(job_id, request.snapshot, request.model_dump_json())
        pool.submit(work, job_id, pf, request)
```

The request is a pydantic model with `extra="forbid"`, a snapshot digest of exactly 64 hex digits,
optional budget locks and a gap between 0 and 10% (lesson 12.4.1). The worker runs lesson 13.1.2's
model, checks the plan with `check` before it reports it, writes the result to S3 and the final
state to SQLite. An infeasible scenario is an answer, `infeasible` with no plan, not an HTTP error
(lesson 12.4.1):

```text
POST /jobs       -> 202, Location /jobs/<id>; fetch at once -> 409
GET /jobs/<id>   -> polled until finished: optimal
GET result       -> optimal, NPV 219,054, bound 219,273, 209 projects
a year outside   -> 422, years outside the plan: [2040]
2027 cut to $2,000k -> infeasible
```

Fetching before the job ends answers **409 Conflict**: the result does not exist yet, and the reply
says the job's state. The result is lesson 13.1.2's run: the same NPV, bound and plan, because the
service uses the same run setting, and lesson 13.1.5's harness already showed that run repeats. A
request with a budget for a year outside the plan is refused before any job exists. The solve
runs in a thread here, which keeps the demo in one process; lesson 12.4.2 showed that a solver crash
in a thread takes the whole process with it, and that a process pool limits it to one job.

<!-- practice 2 -->

## The Frontier Endpoint Returns Only Non-Dominated Plans

The weights of lesson 13.1.3 picked one plan. The board asks what else it could have had, and the
answer is the frontier: plans where no other plan has both more NPV and more risk removed (lesson
8.3.3). The endpoint builds it by the ε-constraint method: the payoff table first (the NPV plan's
risk, and the most risk any plan removes), then the best NPV at evenly spaced risk floors between
them, then drops any point another point dominates:

```python
    b.model.maximize(risk)
    most = best(None)
    b.model.maximize(b.npv)
    low = best(None)["risk"]
    found = []
    for k in range(points):
        p = best(low + (most["risk"] - low) * k / (points - 1))
        if p is not None:
            found.append(p)
```

Each floor is a row added before the solve and deleted after it, so one built model serves every
point (lesson 4.3.4). Five points on GridCap medium:

```text
POST /frontier   -> 200, 5 non-dominated points
     NPV ($k)  risk removed ($k)  projects
      219,125          236,609.8       208
      218,749          283,648.4       215
      217,747          332,827.4       217
      213,473          382,968.4       228
      170,977          433,097.5       246
```

Read it as planners would (lesson 8.3.3): the first $96,000k or so of extra risk removed costs
$1,378k of NPV, the next $50,000k costs $4,274k, and the last $50,000k costs $42,496k. The knee is
between the fourth and fifth points. The weighted-value plan of lesson 13.1.3 (NPV $182,952k, risk
$431,580k) lies in that last, expensive stretch: the board's ratings chose a plan near the risk end.

Two cautions belong in the endpoint's documentation. Each point comes from a solve stopped at the
run setting's 0.1% gap, so a point's NPV is within 0.1% of the best for its floor: the first point
is $71k above the NPV run of lesson 13.1.2, which is two plans inside one gap, not a contradiction.
And five floors give five points, not the whole frontier; lesson 8.3.2's AUGMECON is the exact
method when the board needs every plan.

At the end of the demo S3 holds one snapshot and two results, and the job log holds two rows:

```text
S3 keys: ['results/...', 'results/...', 'snapshots/...']
```

<!-- practice 3 -->

## Summary

- **Snapshots and results live in S3, job states in a local SQLite file.** Content-addressed
  snapshots, re-hashed on read; results written once; states in a `STRICT` table. Tested with moto's
  in-memory S3 and fake credentials, with no network.
- **A job is accepted at once, polled, then fetched.** 202 and an id, 409 until the result exists,
  `infeasible` as an answer; the worker checks every plan before reporting it.
- **The frontier endpoint returns only non-dominated plans.** ε-constraint floors over one built
  model, dominated points dropped; on medium the knee is near $383,000k of risk removed.

## Reference

| Endpoint | Answers |
| --- | --- |
| `POST /snapshots` | 201 `{snapshot, warnings}`; 422 with the gate's errors |
| `POST /jobs` | 202 `{job_id, poll, result}`, with `poll` = `/jobs/<id>` and `result` = `/jobs/<id>/result`, and `Location: /jobs/<id>`; 404 unknown snapshot; 422 bad request |
| `GET /jobs/{id}` | `{job_id, state, finished}`; 404 unknown job |
| `GET /jobs/{id}/result` | the result; 409 before it exists |
| `POST /frontier` | `{snapshot, objectives, points}`: `snapshot` echoes the digest the request named, `objectives` is `["npv", "risk"]`, `points` the non-dominated points sorted by risk removed |

| State | Where | Why there |
| --- | --- | --- |
| snapshot | S3 `snapshots/<digest>.json` | written once, read by every job |
| result | S3 `results/<job id>.json` | written once, when the job ends |
| job state | SQLite `job` table | changes, read on every poll |

**Further reading:** [OR-Tools: MathOpt](https://developers.google.com/optimization/math_opt) (incremental solving: one model changed between solves); [FastAPI: testing](https://fastapi.tiangolo.com/tutorial/testing/) (`TestClient` calls the app with no server running); [moto: getting started](https://docs.getmoto.org/en/latest/docs/getting_started.html) (`mock_aws` as decorator or context manager, and fake credentials so botocore never finds real ones); [boto3 `head_object`](https://docs.aws.amazon.com/boto3/latest/reference/services/s3/client/head_object.html) (metadata without the body, and the error for a missing key); [SQLite STRICT tables](https://www.sqlite.org/stricttables.html) (each value must match its column's declared type).

## Challenges

1. Two clients post the same snapshot at the same moment. What can go wrong in `put_snapshot`
   between `exists` and `put_object`, and why is the result still correct?
2. Move the frontier into a job, like a solve. Which fields does its result need, and what does a
   client poll?
3. The service restarts while a job is `running`. What does the job table say afterwards, and what
   should start-up do about it?

## Design Note: Each Piece of State Where Its Use Puts It

Nothing here was chosen for the technology. Snapshots are immutable and named by content, which is
what an object store does best; results are written once and fetched by id, the same; a job's state
is a small row that changes and is read constantly, which is what a database row is for, and a
local SQLite file is enough for one service. The digest ties them together: every result names the
snapshot it solved, and every snapshot can prove it is still the bytes that were solved.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**service_demo.py.** Runs CIPT Lite as a service against moto's S3 and a temporary SQLite file:
snapshots, a job, bad requests, an infeasible job and the frontier (every section). *Try:* Ask for
three frontier points instead of five. Predict which of the five points remain.

- Program: [service_demo.py](src/service_demo.py)

The milestone's library is `cipt_service.py`.

- Library: [cipt_service.py](src/cipt_service.py)
