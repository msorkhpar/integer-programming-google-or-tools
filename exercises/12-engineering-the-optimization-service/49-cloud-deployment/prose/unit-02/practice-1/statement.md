The vegetation team's trim planner is a CP-SAT model that assigns line-clearance crews to circuits.
It now runs as a Batch job on Fargate: the job definition `trim-solve` and the queue `trim-queue`
exist. What is missing is the call that submits one plan's solve, sized for the plan.

In `trim_jobs.py`, write `submit_trim(batch, queue, definition, plan_id, circuits, limit_s)`. It makes
**one** `batch.submit_job` call and returns the `jobId` Batch gives back. The call carries:

- `jobName`: `job_name(plan_id)`. Batch accepts only letters, digits, hyphens and underscores, with a
  letter or digit first, and at most 128 characters. Replace every other character with `-`, drop
  leading hyphens and underscores, and cut to 128. (`"#7 west/north"` gives `"7-west-north"`.)
- the given `jobQueue` and `jobDefinition`;
- `containerOverrides` with `environment` `PLAN_ID` (the plan id as given), `TIME_LIMIT_S`
  (`str(limit_s)`) and `CPSAT_WORKERS` (the vCPU count, as a string), and `resourceRequirements`
  `VCPU` and `MEMORY` (strings), from `SIZES`: up to 500 circuits, 1 vCPU and 2,048 MiB; up to 5,000,
  2 vCPUs and 8,192 MiB; more, 4 vCPUs and 16,384 MiB. Each is a valid Fargate pair.
- `timeout`: `{"attemptDurationSeconds": ...}`, twice the solver's limit, and never under Batch's
  minimum of 60 seconds.

The tests run against moto and read the parameters your code sent. moto accepts names and timeouts that AWS
refuses (lesson 12.5.4 shows it), so these rules are yours to keep. `SIZES` is given;
about 30 lines remain.
