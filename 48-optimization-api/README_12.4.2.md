# 12.4.2 Long Solves: Submit, Poll, Fetch

The planning tool's team tries lesson 12.4.1's API on the medium portfolio, 400 projects over ten
years, and the request never comes back. The solve is still running, but the browser, and every
proxy between it and the API, has its own timeout, and one of them gives up first. A planner then
clicks again and starts a second solve of the same scenario. The answer is to stop solving inside
the request. This lesson turns each solve into a **job**: one request submits it and gets an id back
at once, later requests poll its status, and a last one fetches the result. It also gives every way
a solve can end its own status, and keeps a crashing solver from taking the service down with it.
(GridCap is fictional; no number in it is real.)

## The Model

The jobs solve the model of lesson 12.4.1, restated here whole. Two things change around it, not in
it: a request may now name any GridCap size, up to the 10,000-project `large`; and every job runs with
a time limit and a relative gap tolerance of 0, so a stop before the proof is visible as a gap.

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
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

The **relative gap** the jobs report compares the best plan found, worth $`v`$, with the solver's
**bound** $`\bar v`$, a value no plan can beat (lesson 3.4.1): $`\text{gap} = (\bar v - v) / |v|`$,
with 1 as the smallest divisor, and never below 0 (`relative_gap` below takes
$`\max(0,\ \bar v - v)`$, so a bound under the value gives 0). A gap of 0 means the plan is proven best.

## A Long Solve Must Not Hold the Request Open

With the solve inside the request, three things go wrong at once:

- **Something times out before the solve ends.** The planner's browser, a proxy, a load balancer:
  each closes a connection that stays silent too long, and the API cannot know which will give up
  first. The solve keeps running for nobody.
- **A retry starts a second solve.** The planner, or the tool, sends the request again, and two
  solves of the same scenario now compete for the machine.
- **Nobody can ask how it is going.** A request either answers or it does not; there is no "still
  running, 40% of the way" in between.

So the API splits one long exchange into three short ones:

| Step | Request | Answer |
| --- | --- | --- |
| submit | `POST /jobs` with the scenario | **202 Accepted** at once, with a job id |
| poll | `GET /jobs/{id}` | the job's status, as often as the caller likes |
| fetch | `GET /jobs/{id}/result` | the result once the job has finished; **409 Conflict** before |

202 Accepted is the HTTP code for "received, and the work will happen later". 409 Conflict says the
request clashes with the current state of the thing it names: the result does not exist yet. The
caller decides how often to poll; every poll is cheap, because it only reads a status.

## BackgroundTasks Runs After the Response, and Keeps No Status

FastAPI has a built-in way to run work after a reply: a path function takes a `BackgroundTasks`
argument and calls `add_task(function, ...)`. The FastAPI docs say these tasks run after the
response is sent, and suggest a bigger tool, Celery, for heavy computation that does not need to
share memory with the app. `background_tasks.py` builds a job API on it, with `time.sleep(1)`
standing in for a one-second solve:

```python
def solve(job_id: str) -> None:
    jobs[job_id] = "running"
    time.sleep(1)
    jobs[job_id] = "optimal"

@app.post("/jobs", status_code=202)
def submit(background: BackgroundTasks) -> dict:
    job_id = f"job-{len(jobs) + 1}"
    jobs[job_id] = "queued"
    background.add_task(solve, job_id)
    return {"job_id": job_id, "status": jobs[job_id]}
```

```text
POST /jobs -> 202 {'job_id': 'job-1', 'status': 'queued'} after 1 s
first poll -> {'job_id': 'job-1', 'status': 'optimal'}
```

The post took a full second, and the first poll already saw the final status. A server sends the
reply first and runs the task afterwards; a `TestClient` hands you the response only after the task
has run too. So a test written this way can never see a job `queued` or `running`, and a slow solve
makes every test that submits one as slow as the solve.

The test client is not the only problem. `BackgroundTasks` gives you no job id, no status, no queue
and no limit on how many solves run at once; the `jobs` dict above is something the code had to add
by hand. Fifty submits would start fifty solves side by side. A job service needs a place that owns
each job, and a pool of workers of a size it chooses.

## A Job Store Keeps Each Job's State, and an Executor Runs the Solves

Python's `concurrent.futures` module has the worker pool: an **executor**. You hand it a function
and its arguments with `submit`, it returns at once with a **future** (an object that will hold the
function's return value, or its exception, once it finishes), and its worker threads run the
submitted calls in order. `JobStore` in `jobs.py` keeps one record per job, by id, around the
executor's futures:

```python
class JobStore:
    """Every job the service has accepted, by id. The executor decides where the solves run."""

    def __init__(self, executor: Executor | None = None, worker=run_job):
        self.executor = executor or ThreadPoolExecutor(max_workers=1)
        self.worker = worker
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()
        self._ids = itertools.count(1)

    def submit(self, request: JobRequest) -> str:
        with self._lock:
            job_id = f"job-{next(self._ids)}"
            self._jobs[job_id] = Job(job_id, request, self.executor.submit(self.worker, request))
        return job_id

    def status(self, job: Job) -> Status:
        if job.future.done():
            return self.outcome(job).status
        return "running" if job.future.running() else "queued"
```

Each decision in these lines:

- **The status is read from the future, never stored twice.** A future knows whether its call has
  started (`running()`) and finished (`done()`). A finished job's status is the one its outcome
  carries. Nothing can go stale, because there is no second copy to update.
- **One worker thread.** `max_workers=1` solves one job at a time, and the others wait in the
  executor's queue. A machine solving one MIP is busy; two at once share the cores and each takes
  longer. The pool's size is the service's choice, and it is the throttle `BackgroundTasks` lacked.
- **A lock around the dict.** Requests are answered on several threads at once (lesson 12.4.1's
  threadpool), so two submits could otherwise interleave their reads and writes. `threading.Lock`
  lets one thread in at a time.
- **Ids come from a counter** (`job-1`, `job-2`, ...), so the programs' output repeats run after
  run. A real service would use `uuid.uuid4().hex`, which nobody can guess or count.

A thread pool can do this only if a solve lets other threads run. Python runs one thread's Python
code at a time (the global interpreter lock), and a native library can hold that lock or release it
while it computes. The next run polls throughout two solves and times every poll.

## Submit Returns 202 and an Id, Poll Returns a Status, Fetch Returns the Result

`job_api.py` puts the three steps on the store. The request model is lesson 12.4.1's, now with every
GridCap size and a longer limit:

```python
class JobRequest(BaseModel):
    """What a planner tool sends to start a job."""

    model_config = ConfigDict(extra="forbid")

    portfolio: Literal["tiny", "small", "medium", "large"]
    budget: dict[int, Annotated[int, Field(ge=0)]] = Field(default_factory=dict)
    time_limit_s: float = Field(default=60.0, gt=0, le=3600)
    highs_threads: int | None = Field(default=None, ge=1)   # a mistake, kept to show why: HiGHS threads are per process
```

(The last field is a mistake that the next section exposes.) The endpoints:

```python
    @app.post("/jobs", status_code=status.HTTP_202_ACCEPTED)
    def submit(request: JobRequest, response: Response) -> JobAccepted:
        job_id = store.submit(request)
        response.headers["Location"] = f"/jobs/{job_id}"
        return JobAccepted(job_id=job_id, status=store.status(find(job_id)),
                           poll=f"/jobs/{job_id}", result=f"/jobs/{job_id}/result")

    @app.get("/jobs/{job_id}", responses={404: {"description": "No job has that id"}})
    def poll(job_id: str) -> JobStatus:
        job = find(job_id)
        now = store.status(job)
        return JobStatus(job_id=job_id, status=now, finished=now in FINISHED)

    @app.get("/jobs/{job_id}/result",
             responses={404: {"description": "No job has that id"}, 409: {"description": "The job has not finished"}})
    def fetch(job_id: str) -> PlanResult:
        job = find(job_id)
        if not job.future.done():
            raise HTTPException(status_code=409, detail=f"job {job_id} is {store.status(job)}; poll /jobs/{job_id}")
        return to_result(job_id, job.request, store.outcome(job))
```

`submit` sets the reply's `Location` header to the job's address, the HTTP convention for "what you
created lives here", and repeats the poll and result paths in the body so a client never builds a
URL by hand. `find` raises 404 for an id the store never gave out. `fetch` returns a `PlanResult`,
the schema of lesson 12.4.3; here, only its status and plan matter. `create_app(store)` builds the
app around a store it is given, so a test can hand it a store with any executor or worker.

`submit_poll_fetch.py` submits the medium portfolio with a 3-second limit, then the small one, and
polls them:

```python
a = client.post("/jobs", json={"portfolio": "medium", "time_limit_s": 3})
b = client.post("/jobs", json={"portfolio": "small"})
```

```text
POST medium -> 202 job_id job-1, poll /jobs/job-1
  Location: /jobs/job-1
POST small  -> 202 {'job_id': 'job-2', 'status': 'queued', 'poll': '/jobs/job-2', 'result': '/jobs/job-2/result'}
poll job-1 -> {'job_id': 'job-1', 'status': 'running', 'finished': False}
poll job-2 -> {'job_id': 'job-2', 'status': 'queued', 'finished': False}
fetch job-1 now -> 409 {'detail': 'job job-1 is running; poll /jobs/job-1'}
every poll during the solves answered in under 0.1 s: True
fetch job-1 -> status time_limit, a plan: True, gap is above zero
fetch job-2 -> status optimal, a plan: True, gap is zero
poll job-9 -> 404 {'detail': "no job 'job-9'"}
```

Both submits returned 202 at once. Job 2 waited `queued` behind job 1, as one worker means. Fetching job 1 early got 409. Every poll
during both solves was answered in under a tenth of a second, so the solve in the worker thread did
not stop the API's threads: MathOpt's solve let them run. (Lesson 12.4.1's `async def` test is the
contrast: there, the blocked thread was the event loop itself.) The medium job stopped at its
3-second limit with a plan and a gap above zero, and the small job's plan was proven, gap zero.

<!-- practice 1 -->

## Every Way a Solve Ends Has Its Own Status

A planner reading a poll must know what to do next, and "done" does not say. Lesson 9.1.1 separates
the ways a solve ends; the service gives each one a status of its own, with a message in the
planner's words:

| Status | When | What the planner does |
| --- | --- | --- |
| `queued`, `running` | the job has not finished | poll again later |
| `optimal` | plan found and proven best | use it |
| `time_limit` | the limit stopped the solve; a plan with its gap, or no plan | use it with its gap, or run longer |
| `infeasible` | proven: no plan meets every rule and budget | change the scenario |
| `failed` | the solve broke; nothing was learned about the scenario | report it; the inputs were not judged |

`outcome_of` reads MathOpt's termination reason and limit (lesson 4.2.2) and writes that table in code:

```python
def outcome_of(result: mathopt.SolveResult, starts: dict[str, int], limit_s: float) -> Outcome:
    """Map MathOpt's termination reason to the service's statuses."""
    reason, limit = result.termination.reason, result.termination.limit
    R = mathopt.TerminationReason
    if reason == R.OPTIMAL:
        npv = result.objective_value()
        return Outcome("optimal", f"Best plan found and proven: NPV ${npv:,.0f}k.", starts, npv,
                       result.best_objective_bound(), relative_gap(npv, result.best_objective_bound()))
    if reason == R.FEASIBLE and limit == mathopt.Limit.TIME:
        npv, bound = result.objective_value(), result.best_objective_bound()
        gap = relative_gap(npv, bound)
        return Outcome("time_limit", f"Stopped at the {limit_s:g} s limit with a plan worth ${npv:,.0f}k; "
                       f"no plan is worth more than ${bound:,.0f}k (gap {gap:.2%}).", starts, npv, bound, gap)
    if reason == R.NO_SOLUTION_FOUND and limit == mathopt.Limit.TIME:
        return Outcome("time_limit", f"No plan found within the {limit_s:g} s limit. This does not mean "
                       "that no plan exists: run again with more time.")
    if reason == R.INFEASIBLE:
        return Outcome("infeasible", "No plan meets every rule and budget. The must-do projects and the "
                       "budgets cannot all be met; check the budgets you changed first.")
    return Outcome("failed", f"The solver stopped without an answer ({reason.name}"
                   f"{', limit ' + limit.name if limit else ''}). The inputs were not judged.")
```

Everything else (unbounded, a numerical error, a limit the service never set) lands in `failed` with
the solver's own reason in the message: none of them says anything about the planner's scenario.
The worker around it, `run_job`, builds and solves the model, and turns any exception into a
`failed` outcome, so a broken solve never escapes into the executor:

```python
def run_job(request: JobRequest) -> Outcome:
    """The worker: build, solve, map. It never raises; an exception becomes a `failed` outcome."""
    try:
        pf = portfolio(request.portfolio)
        pm = build(pf, {**pf.budget, **request.budget})
        params = mathopt.SolveParameters(relative_gap_tolerance=0.0,
                                         time_limit=timedelta(seconds=request.time_limit_s))
        if request.highs_threads is not None:
            params.highs = highs_pb2.HighsOptionsProto(int_options={"threads": request.highs_threads})
        result = mathopt.solve(pm.model, mathopt.SolverType.HIGHS, params=params)
        starts = starts_of(pm, result) if result.has_primal_feasible_solution() else {}
        return outcome_of(result, starts, request.time_limit_s)
    except Exception as error:   # the solver's own reason hides on __context__ in OR-Tools 9.15
        reason = error.__context__ if error.__context__ is not None else error
        return Outcome("failed", f"The solve failed: {reason}. The inputs were not judged.")
```

The `__context__` line is lesson 4.2.4's: in OR-Tools 9.15, a refused solve raises an
`AttributeError` whose real reason is on its `__context__`. `job_outcomes.py` submits six jobs to one
store, one for each way to end, and prints each outcome (numbers that vary from run to run, such as a
time-limited plan's NPV, are masked as `$...k`). The small portfolio's must-do P017 costs $5,310k in
2030 or 2031, so budgets of $5,000k in both years leave it no start:

```python
asks = {
    "small, as given": JobRequest(portfolio="small"),
    "small, 2030-31 cut": JobRequest(portfolio="small", budget={2030: 5000, 2031: 5000}),
    "medium, 1 s limit": JobRequest(portfolio="medium", time_limit_s=1),
    "large, 1 s limit": JobRequest(portfolio="large", time_limit_s=1),
    "small, 2 threads": JobRequest(portfolio="small", highs_threads=2),
    "small, again": JobRequest(portfolio="small"),
}
```

```text
small, as given     optimal     plan: yes  Best plan found and proven: NPV $...k.
small, 2030-31 cut  infeasible  plan: no   No plan meets every rule and budget. The must-do projects and the budgets cannot all be met; check the budgets you changed first.
medium, 1 s limit   time_limit  plan: yes  Stopped at the 1 s limit with a plan worth $...k; no plan is worth more than $...k (gap ...%).
large, 1 s limit    time_limit  plan: no   No plan found within the 1 s limit. This does not mean that no plan exists: run again with more time.
small, 2 threads    failed      plan: no   The solve failed: HighsStatus: kError [INTERNAL]. The inputs were not judged.
small, again        optimal     plan: yes  Best plan found and proven: NPV $...k.
```

Read the two `time_limit` lines and the `infeasible` line together. The large job found no plan, and
its message says that proves nothing; reporting it as `infeasible` would send a planner to cut a
budget rule that may be fine. Only the 2030-31 cut was *proven* to have no plan.

Now the `failed` line. The job asked HiGHS for 2 threads, and the earlier jobs in the same process
had solved with HiGHS's own default. Lesson 4.2.4 showed why that fails: the first HiGHS solve in a
process fixes HiGHS's thread count, and a later solve asking for a different count is refused with
`kError [INTERNAL]`. The worker caught it, the job ended `failed`, and the next job ran normally. The
lesson for the service is about the request model, not the worker: `highs_threads` should never have
been a request field. A setting that belongs to the whole process (HiGHS's threads, and with them
the run's reproducibility, section 10) is the service's configuration, fixed once at start-up. A
request may carry only what can differ from one solve to the next: the scenario and its time limit.

<!-- practice 2 -->

## A Solver Crash Must Not Take the API With It

`run_job` catches every Python exception. It cannot catch a crash in native code: when a C++ solver
reads memory it should not, the operating system ends the whole process with a signal, and every
thread in it, the API's included, dies at once. Lesson 5.2.1 found one such crash in the runner:
a process that has imported PuLP is killed with SIGSEGV on a HiGHS MIP solve
through MathOpt. This module's code never imports `pulp`; `legacy_report.py` plays a dependency that
does, as a report helper might:

```python
import pulp  # noqa: F401  (imported first, as the report helper's module did)

from jobs import JobRequest, Outcome, run_job

def run_job_with_pulp_report(request: JobRequest) -> Outcome:
    return run_job(request)
```

With the solve in a thread of the API's process, `thread_crash.py` runs that service in a child
process (because the crash ends whichever process has it) and reports how it ended:

```text
the service printed: nothing
service process: killed by SIGSEGV
```

The API process is gone, and with it every job in its store, the queued ones included. The fix is to
run each solve in a separate **worker process**. `concurrent.futures.ProcessPoolExecutor` is an
executor whose workers are child processes, and `JobStore` takes any executor, so the API code does
not change. `crash_isolation.py`:

```python
    store = JobStore(ProcessPoolExecutor(max_workers=1), worker=run_job_with_pulp_report)
    client = TestClient(create_app(store))

    job_id = client.post("/jobs", json={"portfolio": "small"}).json()["job_id"]
    store.get(job_id).future.exception()          # wait for the worker to finish, or to die
    print("poll  ->", client.get(f"/jobs/{job_id}").json())
    print("fetch ->", client.get(f"/jobs/{job_id}/result").json()["message"])
    print("the API still answers: GET /jobs/job-1 ->", client.get(f"/jobs/{job_id}").status_code)
```

```text
poll  -> {'job_id': 'job-1', 'status': 'failed', 'finished': True}
fetch -> The worker stopped before answering (BrokenProcessPool). The inputs were not judged.
the API still answers: GET /jobs/job-1 -> 200
the old pool takes no more work: BrokenProcessPool
new pool, next job -> {'job_id': 'job-2', 'status': 'optimal', 'finished': True}
```

The worker process died, and its future ended with a `BrokenProcessPool` exception instead of a
result. `JobStore.outcome` turns that into a `failed` outcome, so the job reads `failed` like any
other failure, and the API kept answering. A pool that lost a worker refuses all further work, so the
program replaces it with a fresh `ProcessPoolExecutor`, and the next job solved normally.

Two details of worker processes. Each worker starts as a fresh Python that imports the program's
main file again, so `crash_isolation.py` keeps its top level to the standard library and its work in
`main()`, behind `if __name__ == "__main__":`. And everything sent to a worker or returned from it
is copied between processes (pickled), so the request and the `Outcome` must be plain data, which a
pydantic model and a dataclass are.

The import order mattered here too. Lesson 5.2.1 shows only that a process which has imported
`pulp` crashes; `pulp_order.py` runs the three orders, each in its own process, on a MIP with one integer variable and one row:

```text
import pulp, then OR-Tools, then solve   killed by SIGSEGV
OR-Tools, then import pulp, then solve   exit 0, objective 2.0
solve, import pulp, solve again          exit 0, objective 2.0 and 2.0
```

Only `pulp` imported before OR-Tools crashed. That is why `legacy_report.py` imports `pulp` at its
top, and why `crash_isolation.py` imports nothing heavy at its own top: a fresh worker process loads
`legacy_report` first. It is also a warning against trusting the order: one reshuffled import line
in a module far from the solver decides whether the service crashes. Keep the two libraries out of
one process instead.

A process per worker is also what lesson 12.5.2 scales up: there, each job runs in
its own container on AWS Batch, the API only records and hands out jobs, and the job store moves from
a dict in memory to storage that survives a restart.

## Summary

- **A long solve must not hold the request open.** Submit answers 202 and an id, poll answers a
  status, fetch answers the result, or 409 before it exists.
- **`BackgroundTasks` runs after the response, and keeps no status.** A `TestClient` returns only
  after the task ran (the post took 1 s), and there is no id, queue or limit.
- **A job store keeps each job's state, and an executor runs the solves.** The status is read from
  the job's future; one worker thread solves while polls answer in under 0.1 s.
- **Every way a solve ends has its own status:** `optimal`, `time_limit` (with or without a plan),
  `infeasible` (proven only), `failed` (the solve broke). Process-wide solver settings, such as
  HiGHS's threads, are the service's configuration, never a request field.
- **A solver crash must not take the API with it.** In a thread it killed the process with SIGSEGV;
  in a `ProcessPoolExecutor` it failed one job, and a new pool ran the next.

## Reference

| Endpoint | Answers |
| --- | --- |
| `POST /jobs` | 202, `{"job_id", "status", "poll", "result"}`, header `Location: /jobs/{id}`; 422 on a bad body |
| `GET /jobs/{id}` | 200, `{"job_id", "status", "finished"}`; 404 for an unknown id |
| `GET /jobs/{id}/result` | 200 with the result (lesson 12.4.3); 409 while queued or running; 404 for an unknown id |

| MathOpt termination (and limit) | Service status |
| --- | --- |
| `OPTIMAL` | `optimal` |
| `FEASIBLE`, limit `TIME` | `time_limit`, with plan and gap |
| `NO_SOLUTION_FOUND`, limit `TIME` | `time_limit`, no plan |
| `INFEASIBLE` | `infeasible` |
| anything else, or an exception, or a dead worker | `failed` |

| Python | What it does |
| --- | --- |
| `ThreadPoolExecutor(max_workers=n)` | n worker threads in this process |
| `ProcessPoolExecutor(max_workers=n)` | n worker processes; a crash breaks the pool, not the API |
| `executor.submit(f, *args)` | queue a call; returns a `Future` at once |
| `future.running()`, `.done()`, `.result()`, `.exception()` | read a call's state and outcome |
| `threading.Lock()` | let one thread at a time into a block |

**Further reading:** the OR-Tools [MathOpt overview](https://developers.google.com/optimization/math_opt);
MathOpt's [`result.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/python/result.py)
(the `TerminationReason` and `Limit` members `outcome_of` maps, `best_objective_bound`, which stays
available without a plan, and the absence of a relative-gap helper, which is why `relative_gap` is
written here); the OR-Tools MathOpt sample
[`integer_programming.py`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py)
(it reads values only after an `OPTIMAL` or `FEASIBLE` termination); FastAPI,
[Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) (tasks run after the
response; heavier work goes to a tool such as Celery),
[Response Status Code](https://fastapi.tiangolo.com/tutorial/response-status-code/),
[Handling Errors](https://fastapi.tiangolo.com/tutorial/handling-errors/) and
[Testing](https://fastapi.tiangolo.com/tutorial/testing/); lesson 4.2.4 (HiGHS's thread count) and
lesson 5.2.1 (the crash after `import pulp`).

## Challenges

1. Add `DELETE /jobs/{id}`, which cancels a queued job. What should it answer for a running one?
   (Look up `Future.cancel` first.)
2. The store keeps every job forever. Write a rule that forgets finished jobs after a day, and say
   what a poll for a forgotten id should answer.
3. Two planners submit the same scenario a minute apart. How could the store notice, and should the
   second get the first job's id? (Lesson 12.4.3's snapshot id helps.)

## Design Note: Where the Job State Lives

This lesson keeps jobs in a dict, in the API's memory. It is the simplest thing that works, and it
has one hard limit: restart the API, and every job, queued, running or finished, is gone, while a
planner may still hold its id. Lesson 12.1.4 stores scenarios and results in SQLite,
and lesson 12.5.2 runs each solve as a container job on AWS. In
that design the API writes a row per job, a separate worker (or AWS Batch) picks it up and writes the
outcome back, and a poll is a database read. The endpoints, statuses and result schema of this
module do not change; only what `JobStore` stands for does. Keeping `create_app(store)` separate from
any one store is what makes that move cheap.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**background_tasks.py.** A job API on FastAPI's `BackgroundTasks`, called through `TestClient`
(*BackgroundTasks Runs After the Response*). *Try:* Make the stand-in solve take 2 seconds. Predict
the post's time and the first poll.

**submit_poll_fetch.py.** Two jobs, one worker: submit, poll while they run, fetch, and an unknown id
(*Submit Returns 202 and an Id*). *Try:* Give the store `ThreadPoolExecutor(max_workers=2)`. Predict
job 2's first status.

**job_outcomes.py.** Six jobs, one for each way a solve ends (*Every Way a Solve Ends Has Its Own
Status*). *Try:* Move the 2-thread job to the front of the list. Predict which jobs fail now.

**thread_crash.py.** The crashing job with the solve in a thread of the API's process (*A Solver
Crash Must Not Take the API With It*). *Try:* Read the program's `SERVICE` text and say which line
never ran.

**crash_isolation.py.** The same job in a worker process, then a new pool for the next job (*A
Solver Crash Must Not Take the API With It*). *Try:* Delete the line that replaces the pool. Predict
the second job's status.

**pulp_order.py.** Runs a MIP solve in three fresh processes, with `import pulp` before OR-Tools,
after it, and between two solves (*A Solver Crash Must Not Take the API With It*). *Try:* Add a
fourth case that solves with SCIP after `import pulp`. Lesson 5.2.1 ran it; predict before you run.

**jobs.py** is the job store, the worker and the status mapping; **job_api.py** the endpoints;
**legacy_report.py** the worker that imports PuLP.

- Program: [background_tasks.py](src/background_tasks.py)
- Program: [submit_poll_fetch.py](src/submit_poll_fetch.py)
- Program: [job_outcomes.py](src/job_outcomes.py)
- Program: [thread_crash.py](src/thread_crash.py)
- Program: [crash_isolation.py](src/crash_isolation.py)
- Program: [pulp_order.py](src/pulp_order.py)
- Library: [jobs.py](src/jobs.py)
- Library: [job_api.py](src/job_api.py)
- Library: [legacy_report.py](src/legacy_report.py)
