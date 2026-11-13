The school district (invented for this practice) locks one repair program per budget year as its
program of record. Each plan is a dict:

```python
{"year": 2028, "state": "Reviewed", "inputs_hash": "a1",
 "run": {"inputs_hash": "a1", "status": "OPTIMAL"}}      # or "run": None
```

`inputs_hash` is the hash of the plan's current inputs, and the run records the hash of the inputs
it was solved on.

Write `lock_refusal(plan_id, plans)` in `guard.py`. It returns `None` when the plan may be locked
now, and otherwise a short reason (any non-empty string). A plan may be locked only when it is in
state `Reviewed`, its run was solved on its current inputs and found an optimal plan, and no other
plan of the same year is already `Locked`. About ten lines.
