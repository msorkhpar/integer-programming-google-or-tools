The planning service is moving its snapshots from a worker's disk to S3, so that every worker, and
every auditor, reads the same inputs. Your milestone writes the store: each snapshot is kept once
under its own content hash and checked again whenever it is read. The tests run against moto's
in-memory S3 with moto's fake credentials: no account, no network. The practice portfolio is
invented for a fictional utility.

A snapshot is a dict in the milestones' shape (`years`, `rate`, `budget`, `region_budget`, `crews`,
`floor`, `projects`), with integer year keys in `budget`, in each region's `region_budget`, in each
program's `crews` and in each project's `npv`. JSON can only write text keys, so the years come out
of S3 as strings.

Write:

| function | contract | lesson |
| --- | --- | --- |
| `canonical(snapshot)` | `json.dumps` with sorted keys, no spaces, ASCII only, as bytes | 12.2.3 |
| `from_json(data)` | the snapshot back from those bytes, with every year key listed above an `int` again | 12.1.1 |
| `put_snapshot(s3, bucket, snapshot)` | the digest is the SHA-256 hex digest of the canonical bytes, and the key is `snapshots/<digest>.json`. Ask `head_object` first; call `put_object` only when nothing is stored under the key. Return the digest | 12.2.3, 12.5.3 |
| `get_snapshot(s3, bucket, digest)` | raise `NotStored` if no object has that key (a `head_object` that answers 404 raises botocore's `ClientError`, whose `response["Error"]["Code"]` is `"404"`); read the object, re-hash its bytes, raise `Corrupted` if they no longer hash to the digest, otherwise return `from_json` of them | 12.2.3 |

Lessons 12.5.3 and 12.5.4 cover the services; the S3 calls you need are `head_object`,
`put_object` and `get_object(...)["Body"].read()`, each with `Bucket=` and `Key=`. About thirty
lines.
