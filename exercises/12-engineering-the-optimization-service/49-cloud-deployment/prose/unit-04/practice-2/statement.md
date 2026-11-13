This lesson found that moto accepted a job name and a timeout that AWS Batch refuses. The service
will check every `SubmitJob` request itself before sending it, so the moto suite can test the checks
and production gets them too.

In `submit_check.py`, write `problems(request)`. `request` is the keyword arguments of a
`batch.submit_job` call, as a dict. Return every rule it breaks, as these exact texts, in this order:

1. `jobName 'NAME' is not a valid job name` unless the name is 1 to 128 characters of letters,
   digits, hyphens and underscores, with a letter or digit first.
2. `timeout N s is under 60 s` if `timeout.attemptDurationSeconds` is given and under 60.
3. `retry attempts N is outside 1-10` if `retryStrategy.attempts` is given and outside 1 to 10.
4. Under `containerOverrides.resourceRequirements`: `VCPU and MEMORY must be given together` if only
   one of the two is there; otherwise, if both are, `VCPU V with MEMORY M is not a Fargate size`
   (with the values as given) unless the memory is one `FARGATE` lists for that vCPU count. Both
   values are strings, as boto3 sends them; the vCPU count may be `"0.5"`.
5. `environment variable NAME is set twice` for each repeat of a name in
   `containerOverrides.environment`.

A request without a timeout, retry strategy, size or environment has nothing to check there.
`FARGATE` (the table of lesson 12.5.2) and the name pattern `NAME` are given; about 20 lines remain.
