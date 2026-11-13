The trim planner's job role gets its own policy file, and the platform team wants each new policy
checked in CI against the requests the job will make, and the ones it must never make. The lesson's
`allows` knew only Allow statements written as lists. This one must handle what real policy files
contain.

In `iam_check.py`, write `allowed(policy, action, resource)` for one identity policy document:

- A statement **applies** when one of its `Action` patterns matches the action **and** one of its
  `Resource` patterns matches the resource. `Action` and `Resource` may each be a list of patterns or
  a single string (one pattern).
- In a pattern, `*` matches any run of characters (also none) and `?` exactly one character; every
  other character matches only itself. Actions match in any letter case (`S3:getobject` is
  `s3:GetObject`); resources match case exactly.
- The answer is `True` only if some applying statement has `"Effect": "Allow"` and none has
  `"Effect": "Deny"`. An explicit Deny always wins; with no applying statement, the request is denied.

This is a model of one policy, as the lesson's is: no conditions, no other policy types. The helper
names `matches`, `as_list` and `applies` are declared for you; about 10 lines remain.
