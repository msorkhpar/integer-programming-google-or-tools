GridCap's asset team uploads condition surveys: a survey id, a region and a list of readings, one per
asset. The risk model reads them, and an auditor must be able to fetch exactly the survey a risk
score used. Store them in S3 the way the lesson stores snapshots.

In `survey_store.py`, write:

- `canonical(survey)`: the survey as bytes, so equal content gives equal bytes. The `readings` list
  has no meaningful order: sort it by `asset_id`. Then `json.dumps` with sorted keys, separators
  `(",", ":")` and `ensure_ascii=True`, encoded as ASCII.
- `put_survey(s3, bucket, survey)`: store the canonical bytes at `survey_key(digest)`, where the
  digest is their SHA-256 in hex, and return the digest. The write must never replace an object
  that is already at the key: use S3's conditional write. A refusal because the key is taken
  (`PreconditionFailed`) is not an error; any other error (a missing bucket, say) must propagate.
- `get_survey(s3, bucket, digest)`: `(survey, "ok")` if the object's bytes hash to `digest`;
  `(None, "corrupted")` if they do not; `(None, "missing")` if there is no object (`NoSuchKey`).
  Any other error propagates.

The tests run against moto with fake credentials. `survey_key` is given; about 25 lines remain.
