The trim team now wants the API to choose. A request lists the circuits, each with its trim `cost`
($k) and its `risk_reduction` (expected outage-minutes avoided per year), the season's `budget`, and
the ids of circuits that `must_trim` (a regulator's order, say). The answer is the set of circuits
that avoids the most outage-minutes while the total cost stays within the budget, with every
must-trim circuit in it.

Write the endpoint `select` in `trim_select.py`. The request and response models are written.

1. Write the formulation first, on paper: the sets, the parameters with their units, a variable per
   circuit with its domain, the objective with its sense, and each constraint with a label. Then
   build it with MathOpt and solve with HiGHS.
2. Answer `status: "optimal"` with `chosen` (circuit ids, sorted), their total `cost` and total
   `risk_reduction`.
3. When no selection can trim every must-trim circuit within the budget, the request was still a
   good request: answer 200 with `status: "infeasible"`, no circuits, and zeros.
4. A `must_trim` id that names no circuit in the request is a bad request: raise an
   `HTTPException` with status 422 before building anything. So is a request that lists the same
   `circuit_id` twice: `chosen` could not say which of the two was meant, so answer 422 for it too.

The tests check the answers to small requests, so any correct formulation passes.
