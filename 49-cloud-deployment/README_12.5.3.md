# 12.5.3 S3 and a Local SQLite File for Snapshots and Results

Lesson 12.2.3 stored each snapshot as a file named by its digest, on one machine's disk. Lesson
12.1.4 stored scenarios and runs in a SQLite file. Now the solve runs in a container that Batch
starts on a machine nobody chose (lesson 12.5.2), and that container cannot see the API's disk. The
snapshot it reads and the result it writes must live somewhere both can reach, durably, and the
regulator's question from lesson 12.2.3 still stands: which exact inputs produced the plan of
record? This lesson splits storage in two. **Amazon S3**, AWS's object store, holds the content:
every snapshot and every result, written once under a key derived from what it is. A **local SQLite
file** next to the API holds one small row per run that points at those objects, so the questions
planners ask ("every run of this snapshot", "what is still waiting") are SQL queries. (GridCap is
fictional; no number in it is real.)

S3 here is moto's fake (lesson 12.5.4); no AWS is reached. A few terms: S3 stores **objects** (a
body of bytes plus a little metadata) in a **bucket**, each under a **key**, a string such as
`results/730c…/run-0007.json`. The slashes are only characters of the key; listing by a **prefix**
such as `results/` is how a "folder" is read.

## The Model

The runs stored here solve the model of lesson 12.5.2, unchanged and restated here whole.

**Sets.** $`Y`$ the plan's years; $`P`$ the projects; $`T_i`$ the start years of project $`i`$
($`e_i \le t \le l_i`$, work ending by $`\max Y`$); $`M`$ the must-do projects; $`\mathcal{G}`$ the
alternative groups; $`C`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$; $`Q`$ the
programs ($`q(i)`$ of project $`i`$); $`R`$ the regions ($`r(i)`$ of project $`i`$).

**Parameters.** $`c_{i,k}`$, spend in the $`k`$-th year of work ($k), $`d_i`$ years of work,
$`\text{capex}_i = \sum_k c_{i,k}`$; $`\text{npv}_{i,t}`$ ($k); $`m_i`$ crew-months per year of
work; $`B_y`$ budgets ($k); $`K_{q,y}`$ crew-months; $`\text{floor}_r`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$, $`t \in T_i`$.

**Objective.**

```math
\max \; \sum_{i \in P} \sum_{t \in T_i} \text{npv}_{i,t}\, x_{i,t}
```

**Constraints.**

```math
\begin{aligned}
\sum_{t \in T_i} x_{i,t} &\le 1 && \forall i \in P \setminus M && \text{(once}_i) \\
\sum_{t \in T_i} x_{i,t} &= 1 && \forall i \in M && \text{(must}_i) \\
\sum_{i \in g} \sum_{t \in T_i} x_{i,t} &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g) \\
\sum_{u \in T_c,\, u \le t} x_{c,u} &\le \sum_{s \in T_{p(c)},\, s \le t - L_c} x_{p(c),s} && \forall c \in C,\ t \in T_c && \text{(after}_{c,t}) \\
\sum_{i \in P} \sum_{t \in T_i,\, 0 \le y - t < d_i} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{i:\, q(i) = q} \ \sum_{t \in T_i,\, 0 \le y - t < d_i} m_i\, x_{i,t} &\le K_{q,y} && \forall q \in Q,\ y \in Y && \text{(crews}_{q,y}) \\
\sum_{i:\, r(i) = r} \ \sum_{t \in T_i} \text{capex}_i\, x_{i,t} &\ge \text{floor}_r && \forall r \in R && \text{(floor}_r)
\end{aligned}
```

A stored result keeps the solution as `starts`, one entry per funded project: the pair $`(i, t)`$
with $`x^*_{i,t} = 1`$, and its NPV.

## A Snapshot's Key Is Its Digest, So Equal Content Is One Object

The store keeps lesson 12.2.3's idea and moves it to S3: a snapshot's key is
`snapshots/sha256/<digest>.json`, where the digest is the SHA-256 of the snapshot's canonical form,
and the object's body is those canonical bytes. `S3Store.put_snapshot`:

```python
    def put_snapshot(self, snap: Snapshot) -> str:
        """Store a validated snapshot under its digest; return the digest. Equal content is stored once."""
        data = canonical(snap)
        digest = hashlib.sha256(data).hexdigest()
        self._create(snapshot_key(digest), data)
        return digest
```

Results go under the snapshot they solved, one object per run: `results/<digest>/<run_id>.json`.
Every result of one snapshot is then one prefix listing away, and the key can be computed by anyone
who knows the run and its snapshot, which lesson 12.5.2's poll relies on.

`s3_snapshots.py` stores GridCap small, then the same export pretty-printed, as a second planner
re-sending it would:

```text
digest: 730c8b40b1eb | re-sent export, same digest: True | objects: ['snapshots/sha256/730c8b40b1ebdabec854a5b7157ef9dd9208c223e73c7f18020d15f5a00bf520.json']
```

One object, with lesson 12.2.3's digest: moving the store to S3 did not change a single id. A real
change of content gets a new key and a second object. This lesson calls it the **lean-2029**
snapshot: GridCap small with only its 2029 budget cut, from $8,760k to $7,000k. (Lesson 12.2.3's v2
made the same cut and also committed P024, so it is a different snapshot with a different digest.)

```text
lean 2029: new digest 60c107fc884c | objects: 2
```

## Every Write Is Conditional: S3 Refuses to Replace an Object

A plain `put_object` replaces whatever is at the key. Two workers retrying the same result, or a
script "fixing" a snapshot, would overwrite history without a trace. S3 supports **conditional
writes**: with the header `If-None-Match: *`, the S3 documentation says a write succeeds only if no
object exists at the key, and otherwise fails with `412 Precondition Failed`; of two such writes
racing for one key, the first to finish wins. boto3 sends it as `IfNoneMatch="*"`:

```python
    def _create(self, key: str, data: bytes) -> bool:
        """Write `data` at `key` unless an object is already there. True if this call wrote it."""
        try:
            self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, IfNoneMatch="*",
                               ContentType="application/json")
        except ClientError as error:
            if error_code(error) == "PreconditionFailed":
                return False
            raise
        return True
```

```text
conditional overwrite: PreconditionFailed 412
```

The two callers read the refusal differently, and that is the point of returning a flag:

- **A snapshot that already exists is a success.** Same key means same content, so there is nothing
  to write. `put_snapshot` ignores the flag.
- **A result that already exists is an error.** A run writes one result; a second write for the same
  run is a bug or a race, and must not replace the first:

```text
result written: results/730c8b40b1ebdabec854a5b7157ef9dd9208c223e73c7f18020d15f5a00bf520/run-0007.json
second result for run-0007 refused: results/730c8b40b1ebdabec854a5b7157ef9dd9208c223e73c7f18020d15f5a00bf520/run-0007.json already holds a result
```

S3 also has **strong read-after-write consistency** (its documentation states it for every PUT and
DELETE of an object): once a write returns, every read sees it. So a poll that finds no result
object right after the worker wrote one cannot happen.

## Every Read Re-Hashes, and Versioning Keeps What an Overwrite Replaced

A conditional write protects against callers that use it. Anyone with write permission can still
call `put_object` without the condition. So, as in lesson 12.2.3, `get_snapshot` hashes the bytes it
reads and compares the result with the key before trusting them:

```python
        data = self.s3.get_object(Bucket=self.bucket, Key=snapshot_key(digest))["Body"].read()
        found = hashlib.sha256(data).hexdigest()
        if found != digest:
            raise Corrupted(f"snapshot {digest[:12]} now hashes to {found[:12]}")
```

The program overwrites the lean-2029 snapshot, unconditionally, with its 2029 budget changed from
$7,000k to $7,900k in the stored bytes, then reads it:

```text
read after an overwrite: refused, snapshot 60c107fc884c now hashes to 4a1cabf8704e
```

Refusing the edit protects the next solve; it does not bring the inputs back. **Versioning** does.
The bucket was created with versioning on (lesson 12.5.5 sets it in Terraform), and the S3
documentation explains that a versioned bucket keeps every version of an object: an overwrite adds a
new current version, and a delete adds a delete marker. The original snapshot is still there:

```text
versions kept: 2 | the earlier one re-hashes to its key: True
```

The earlier version still hashes to its key, so the inputs of every run that read it can be
recovered and checked. The two defences work together: the digest detects a change, and versioning
keeps what the change replaced. Lesson 12.5.5 also blocks the IAM permissions that would allow the
overwrite in the first place.

<!-- practice 1 -->

## A Local SQLite File Indexes the Runs, and S3 Holds Their Content

S3 answers "give me this key" and "list this prefix". It does not answer "which runs of snapshot
`730c…` finished optimal, best NPV first". A query like that wants rows. So the API keeps a SQLite
file, as lesson 12.1.4 did, with one row per run that points at its objects:

```python
SCHEMA = """
CREATE TABLE run (
    run_id          TEXT PRIMARY KEY,
    snapshot_digest TEXT NOT NULL CHECK (length(snapshot_digest) = 64),
    snapshot_key    TEXT NOT NULL,
    batch_job_id    TEXT,
    status          TEXT NOT NULL
                    CHECK (status IN ('submitted', 'optimal', 'time_limit', 'infeasible', 'failed')),
    result_key      TEXT,
    npv             INTEGER,
    CHECK ((status = 'submitted') = (result_key IS NULL))
) STRICT;
```

What goes where follows lesson 12.1.4's rule, "store as a whole what is used as a whole; store as
rows what is queried":

- **The snapshot and the result are content**, read whole by the worker and by the API. They live in
  S3. The index stores only their keys, never a copy, so the two cannot disagree.
- **The run's status and NPV are what planners filter and sort by.** They are columns.
- **The last `CHECK` ties the two together:** a run is `submitted` exactly when it has no result key.
  A finished status without a pointer to its result is refused by the database itself, whoever writes.

The connection is opened with lesson 12.1.4's `connect` (foreign keys on before any transaction,
explicit transactions). A poll is `refresh`: if the row still says `submitted`, look for the result
object at the key the run's digest and id give, and record it if it is there:

```python
def refresh(conn: sqlite3.Connection, store: S3Store, run_id: str) -> str:
    """A poll: if the run still waits, look for its result object in S3, and record it when it is there."""
    row = conn.execute("SELECT snapshot_digest, status FROM run WHERE run_id = ?", (run_id,)).fetchone()
    if row["status"] == "submitted":
        key = result_key(row["snapshot_digest"], run_id)
        result = store.get_result(key)
        if result is not None:
            finish(conn, run_id, key, result)
```

`finish` is an `UPDATE ... WHERE run_id = ? AND status = 'submitted'`, so a second poll that finds
the same result changes nothing (lesson 12.1.4's version check in the `WHERE` clause, here on the
status). `run_index_demo.py` indexes three runs (two of GridCap small, one of the lean-2029 snapshot), lets the
worker finish two of them, and polls all three:

```text
polls: {'run-0007': 'optimal', 'run-0008': 'submitted', 'run-0009': 'optimal'}
{'run_id': 'run-0007', 'snapshot': '730c8b40b1eb', 'status': 'optimal', 'npv': 22741}
{'run_id': 'run-0008', 'snapshot': '730c8b40b1eb', 'status': 'submitted', 'npv': None}
{'run_id': 'run-0009', 'snapshot': '60c107fc884c', 'status': 'optimal', 'npv': 22352}
finish run-0008 without a result key: CHECK constraint failed: (status = 'submitted') = (result_key IS NULL)
```

The lean 2029 budget costs $389k of NPV ($22,741k against $22,352k), and the query that shows it never
opened a result object.

**The file stays with the API.** SQLite keeps a whole database in one local file with no server
(lesson 12.1.4), which suits one API process that owns it. The Batch
container and the Lambda function never touch the file (lesson 12.5.2's design note); they write to
S3, and the API records what they wrote.

## The Index Can Be Rebuilt From S3, Except for Runs Still Waiting

Because every result object carries its run id, snapshot digest, status and NPV, S3 holds everything
the index says about a finished run. If the SQLite file is lost, a listing of `results/` rebuilds it.
`rebuild` uses a **paginator**, because a single list call returns at most 1,000 keys (lesson 12.5.4
shows what happens without one):

```python
    pages = store.s3.get_paginator("list_objects_v2").paginate(Bucket=store.bucket, Prefix="results/")
```

The program deletes the index file, makes a new one and rebuilds it:

```text
rebuilt from S3: 2 rows
[('run-0007', 'optimal', 22741), ('run-0009', 'optimal', 22352)]
```

Two rows, not three. `run-0008` had been submitted but had no result yet, and nothing in S3 says it
exists. A run that is still waiting is known only to the index and to the services running it (its
Batch job, or its Step Functions execution, lesson 12.5.2). So the index file is not disposable: back
it up, and after a rebuild, ask Step Functions for the executions still running to recover the
waiting runs. What S3 guarantees is narrower and still valuable: no finished run, and no input any
run read, can be lost with the file.

<!-- practice 2 -->

## Summary

- **A snapshot's key is its digest, so equal content is one object.** Results live under the
  snapshot they solved: `results/<digest>/<run_id>.json`.
- **Every write is conditional.** `IfNoneMatch="*"` makes S3 refuse to replace an object (412); an
  existing snapshot is fine, an existing result is an error.
- **Every read re-hashes, and versioning keeps what an overwrite replaced.**
- **A local SQLite file indexes the runs, and S3 holds their content.** Keys and queried fields are
  columns; a `CHECK` ties `submitted` to "no result key"; a poll records a result it finds.
- **The index can be rebuilt from S3, except for runs still waiting.**

## Reference

| Key | Holds | Written by |
| --- | --- | --- |
| `snapshots/sha256/<digest>.json` | the snapshot's canonical bytes | the API, once per content |
| `results/<digest>/<run_id>.json` | the run's result: status, NPV, starts or a message | the worker, or the failure function |

| boto3 S3 call | What it does |
| --- | --- |
| `put_object(Bucket, Key, Body, IfNoneMatch="*")` | write only if no object exists; else `PreconditionFailed` (412) |
| `get_object(Bucket, Key)["Body"].read()` | the object's bytes; `NoSuchKey` if absent |
| `get_paginator("list_objects_v2").paginate(Bucket, Prefix)` | every key under a prefix, page by page |
| `put_bucket_versioning(..., {"Status": "Enabled"})` | keep every version of every object |
| `list_object_versions(Bucket, Prefix)` | the versions, with `IsLatest` |

| Index function | SQL it runs |
| --- | --- |
| `record_submitted` | `INSERT` a `submitted` row |
| `finish` | `UPDATE ... WHERE run_id = ? AND status = 'submitted'` |
| `refresh` | read the row; if waiting, look for the result object; `finish` if found |
| `rebuild` | one `INSERT` per result object listed in S3 |

**Further reading:** OR-Tools, the [MathOpt overview](https://developers.google.com/optimization/math_opt)
(the solve whose results are stored); Amazon S3,
[Conditional writes](https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html)
(`If-None-Match`, 412, racing writes),
[What is Amazon S3?](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html) (strong
read-after-write consistency), [Versioning](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
and [ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) (1,000
keys per call); boto3, [Paginators](https://docs.aws.amazon.com/boto3/latest/guide/paginators.html);
Python, [`sqlite3`](https://docs.python.org/3/library/sqlite3.html); lessons 12.1.4 and 12.2.3.

## Challenges

1. Add a query for "the best finished run of each snapshot" in SQL, and say what it should return
   for a snapshot whose only run is still waiting.
2. Planners want to delete a scenario's draft runs. Which objects may go, which must stay, and what
   does versioning do to a delete?
3. Change `rebuild` so that it can run on an index that already has rows, without duplicating any.

## Design Note: Two Stores, One Direction of Truth

Two stores invite the question "which one is right?" Here the answer is fixed by direction: S3 is
written first and never changed, and the index only ever points at S3 objects that exist. A row can
lag behind S3 (a result written that no poll has recorded yet), but never run ahead of it, because
`finish` takes its key from an object it just read. A rebuild repairs lag; nothing has to repair a
row that points at nothing. Keeping the index to keys and queried fields, never copies of content,
is what keeps that direction simple.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**s3_snapshots.py.** Snapshots by digest, a conditional overwrite, a result written twice, an
unconditional overwrite caught on read, and versioning (*A Snapshot's Key Is Its Digest* through
*Versioning Keeps What an Overwrite Replaced*). *Try:* Turn versioning off. Predict the last line.

**run_index_demo.py.** Three runs indexed, two finished, polled, queried, and the index rebuilt from
S3 (*A Local SQLite File Indexes the Runs*, *The Index Can Be Rebuilt*). *Try:* Let the worker finish
`run-0008` before the file is deleted. Predict the rebuilt row count.

**s3_store.py** is the snapshot and result store; **run_index.py** the SQLite index.

- Program: [s3_snapshots.py](src/s3_snapshots.py)
- Program: [run_index_demo.py](src/run_index_demo.py)
- Library: [s3_store.py](src/s3_store.py)
- Library: [run_index.py](src/run_index.py)
