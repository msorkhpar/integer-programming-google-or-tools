The vegetation team is writing its own CI workflow for the trim planner. Before any workflow in the
organisation may run, a lint step reads it, parsed by PyYAML, and refuses the habits this lesson
warns about.

In `workflow_lint.py`, write `lint(workflow)`. `workflow` is the parsed file (a dict; remember that
PyYAML reads the key `on` as `True`, which this check does not need). Return the sorted findings,
each once, as these exact texts:

- `workflow: no top-level permissions` when the workflow has no `permissions` key, and
  `workflow: permissions write-all` when it is the string `write-all`. A job whose `permissions` is
  `write-all` gives `JOB: permissions write-all`.
- `JOB: REF is not pinned to a commit SHA` for every `uses:` value not of the form
  `owner/name@` followed by a full 40-character lower-case hex SHA. A local action, whose `uses`
  starts with `./`, is code in the same repository and needs no pin.
- `JOB: uses secret NAME` for every `secrets.NAME` found anywhere in a job's steps (`run`, `with`,
  `env`, at any depth), except `GITHUB_TOKEN`, the token GitHub gives every job.
- `JOB: id-token: write without an AWS credentials step` when a job's permissions grant
  `id-token: write` and none of its steps uses `aws-actions/configure-aws-credentials`. A job with
  no `permissions` key of its own gets the workflow's, so a workflow-level `id-token: write` counts
  for it; a job that sets its own `permissions` uses only those. (The `write-all` finding, above,
  looks only at what each level writes itself.)

`PINNED`, `SECRET`, `AWS_STEP` and `texts` (every string inside a value) are given; about 20 lines
remain.
