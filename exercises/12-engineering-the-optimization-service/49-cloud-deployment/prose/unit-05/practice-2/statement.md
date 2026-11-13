The vegetation team's Terraform puts its buckets inside a module and sometimes has to delete a
scratch bucket on purpose. Their CI needs a gate that reports what a plan does and blocks only the
deletes nobody approved.

In `plan_gate.py`, write `gate(plan, protected, allowed=frozenset())`. `plan` is the JSON of
`terraform show -json` (this lesson): a `resource_changes` list whose entries have an `address`, a
`type`, a `mode` (`"managed"`, or `"data"` for a data source) and `change.actions`. Return a pair:

- the **sorted** addresses to block: every change whose `type` is in `protected`, whose actions
  delete it (a plain delete, or a replacement in either order), and whose address is not in
  `allowed`. A resource inside a module has an address such as
  `module.storage.aws_s3_bucket.runs`; its `type` is still `aws_s3_bucket`.
- a dict counting the changes by verb, from `VERBS`: `["delete", "create"]` and
  `["create", "delete"]` are one `replace` each. Every change counts, data-source reads included.
  Verbs with no change are left out.

`VERBS` is given; about 8 lines remain.
