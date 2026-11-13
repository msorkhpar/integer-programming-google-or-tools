GridCap's report-publishing state machine has a Task state that posts a finished plan to the
planners' reporting system. That system throttles, times out and rejects bad input, and the
operations team wants to know, before deploying, what the state will do for a given run of errors.
Write a function that answers it, by the rules the lesson quotes from the Step Functions
documentation.

In `error_routing.py`, write `route(state, errors)`. `state` is a Task state's dict (its `Retry` and
`Catch` lists may be missing). `errors` are the error names of consecutive failed attempts; if the
state is still going after the last one, the next attempt succeeds. Return the list of what happened,
one entry per error, using `"retry"`, `"catch:<Next>"` and `"fail"`, and `"succeeded"` at the end if
the state got there. Stop at the first catch or fail.

- For each error, the **first** retrier whose `ErrorEquals` names it decides. If that retrier has
  retries left (`MaxAttempts`, 3 when missing; 0 means never), it is a retry, counted against that
  retrier only.
- Otherwise (no retrier names the error, or the first one that does is used up) the first catcher
  whose `ErrorEquals` names the error gives `catch:<its Next>`. With no such catcher, `fail`.
- Write `matches(names, error)`: `States.ALL` matches any error; `States.TaskFailed` matches any error
  except `States.Timeout`; any other name matches only itself.

Waiting times (`IntervalSeconds`, `BackoffRate`) do not change the route; ignore them. About 20
lines remain.
