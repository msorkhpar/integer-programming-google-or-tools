The school district's (invented for this practice) facility planners edit repair plans from
several laptops at once. A plan is a dict such as `{"roofs": 400, "boilers": 250}`. Two planners
who read the same plan and both save would lose one of the two changes, so the store keeps a
version number per plan, starting at 1.

Finish `Store` in `store.py`:

- `read(plan_id)` returns the plan and its version. A caller may change the dict it gets back as
  much as it likes; that must not change the stored plan.
- `save(plan_id, read_version, plan)` stores `plan` and returns the new version, one more than
  before, if the plan is still at `read_version`. Otherwise it returns `None` and stores nothing.
  A caller who keeps changing its dict after a save must not change the stored plan either.

About six lines.
