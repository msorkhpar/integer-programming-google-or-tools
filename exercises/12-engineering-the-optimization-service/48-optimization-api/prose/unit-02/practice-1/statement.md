The crew-roster optimizer assigns line crews to weeks of work, and on a full season it runs for
several minutes. The scheduling tool cannot hold an HTTP request open that long, so it needs a job
API: submit a roster request, poll its status, fetch the result when it is done.

In `crew_jobs.py`, write `create_app(solve, workers=1)`. `solve` is given to you by the caller (the
tests pass small stand-ins); it takes a `RosterRequest`, may take minutes, returns a dict with a
`"status"` key, and may raise. The API:

- `POST /jobs` with a `RosterRequest` body answers **202** at once with `{"job_id": ..., "status":
  "queued"}`. The solve runs on one of `workers` worker threads, never inside the request.
- `GET /jobs/{job_id}` answers `{"job_id", "status", "message", "ahead"}`. For a queued job,
  `ahead` is how many queued jobs were submitted before it, so the tool can say "2 jobs ahead of
  yours"; the job being solved is not counted, and `ahead` is 0 for any job not queued. The status
  is `"queued"` until a worker starts the job, `"running"` while it solves, then the `"status"` of the dict `solve`
  returned. If `solve` raises, the status is `"failed"` and the message carries the exception's
  text; the worker goes on to the next job.
- `GET /jobs/{job_id}/result` answers 200 with the dict `solve` returned (or `{"status": "failed",
  "message": ...}` for a failed job), and **409** while the job is queued or running.
- An id the API never gave out gets **404** on both GET paths.

Unlike the lesson's store, this one keeps each job's status in a record the worker updates itself,
so the status says what the worker has done rather than what the executor reports. Guard the shared
dict with a lock: the endpoints and the worker threads touch it at the same time. The job record, the lock, the pool, the submission order and a `find` that answers 404 are
written; about 30 lines remain.
