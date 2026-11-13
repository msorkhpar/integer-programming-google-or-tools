# 12.5.4 Testing AWS Code Against moto

Every program in lessons 12.5.1 to 12.5.3 called S3, Batch or Step Functions, and none of them
reached AWS. They ran against **moto**, a Python library that imitates AWS services inside the test
process: boto3 sends its requests as usual, and moto answers them from memory, with AWS's response
shapes and error codes. That is how GridCap's service can be tested on every commit, offline, in
seconds, with no account and no bill. It is also how a test suite can pass while the code is wrong,
if you do not know what moto checks and what it does not. This lesson sets up moto safely, writes
pytest tests with it, and maps its limits with programs that ran. (GridCap is fictional; no number
in it is real.)

No model is built or changed here: the code under test stores and runs the model of lesson 12.5.2.

## Fake Credentials Come First, So No Test Can Sign as Anyone

boto3 signs every request with credentials it finds in the environment, a config file, or the
machine's role. A test machine may have real ones: a developer's laptop usually does. If a test then
creates a client outside moto's mock, by mistake, its requests are signed as that developer and sent
to AWS. moto's documentation therefore recommends setting fake credentials before anything else, in
a fixture. The module's `fake_aws.py` sets the five variables it lists, and points boto3 at no config
file:

```python
FAKE_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_SECURITY_TOKEN": "testing",
    "AWS_SESSION_TOKEN": "testing",
    "AWS_DEFAULT_REGION": "us-east-1",
}
```

`moto_safety.py` first runs a child process with no AWS variables at all, as a test run on a clean
machine would, and calls S3 without moto; then it calls S3 inside the mock:

```text
no credentials, no mock: NoCredentialsError: Unable to locate credentials
fake credentials: ['AWS_ACCESS_KEY_ID', 'AWS_DEFAULT_REGION', 'AWS_SECRET_ACCESS_KEY', 'AWS_SECURITY_TOKEN', 'AWS_SESSION_TOKEN']
inside the mock: ['gridcap-runs-example']
account moto reports: 123456789012
```

Without credentials boto3 refuses to sign, before any request leaves. With the fake ones, a request
that escaped the mock would be signed with the key `testing`, which belongs to no one, and AWS would
reject it. Inside the mock, the bucket exists only in moto's memory, and the account is moto's
placeholder `123456789012`. No real account id, key or region tied to a person appears anywhere in
the course's code or output.

## mock_aws Gives Every Test a Fresh, Empty AWS

`mock_aws` works as a decorator, a context manager, or with `start()` and `stop()`. Each time it
starts, the fake AWS is empty; when it stops, everything in it is gone. The moto documentation's
advice is to start it before creating any boto3 client, so that no client is set up against the real
endpoints. In pytest, fixtures express all of this, and they usually live in `conftest.py`:

```python
@pytest.fixture
def aws_credentials(monkeypatch):
    """Fake credentials for every test, so no test can sign a request as anyone real."""
    for name, value in FAKE_CREDENTIALS.items():
        monkeypatch.setenv(name, value)


@pytest.fixture
def s3(aws_credentials):
    """A fresh, empty fake S3 per test; the client is made inside the mock."""
    with mock_aws():
        yield boto3.client("s3")


@pytest.fixture
def store(s3):
    s3.create_bucket(Bucket="gridcap-test")
    return S3Store(s3, "gridcap-test")
```

The chain does the ordering: `store` needs `s3`, which needs `aws_credentials`, so the credentials
are set, then the mock starts, then the client is made, then the bucket. `monkeypatch` undoes the
variables after each test. The tests themselves read like tests of any other code:

```python
def test_an_overwritten_snapshot_is_refused(store, s3, tiny):
    digest = store.put_snapshot(tiny)
    s3.put_object(Bucket="gridcap-test", Key=snapshot_key(digest), Body=b'{"schema_version":1}')
    with pytest.raises(Corrupted):
        store.get_snapshot(digest)
```

`pytest_with_moto.py` runs its four tests with pytest and prints each outcome:

```text
test_equal_content_is_one_object              passed
test_an_overwritten_snapshot_is_refused       passed
test_a_missing_result_is_none                 passed
test_each_test_starts_with_an_empty_bucket    passed
```

The last test is the isolation check: the test before it stored snapshots, and this one finds an
empty bucket, because each test's `s3` fixture started its own mock.

## moto Returns AWS's Errors and Pages, So Test Them

What moto does well is the contract of each call: the shapes of responses, the error codes, the
paging. Code that handles those can be tested exactly. `moto_limits.py` stores 1,005 result objects
and lists them two ways:

```python
    one = s3.list_objects_v2(Bucket=BUCKET, Prefix="results/")
    print("one list call:", one["KeyCount"], "keys, IsTruncated", one["IsTruncated"])
    pages = s3.get_paginator("list_objects_v2").paginate(Bucket=BUCKET, Prefix="results/")
    print("paginator:", sum(len(p.get("Contents", [])) for p in pages), "keys")
```

```text
one list call: 1000 keys, IsTruncated True
paginator: 1005 keys
```

The S3 API reference says a `ListObjectsV2` call returns at most 1,000 keys, sets `IsTruncated`,
and hands back a continuation token for the rest. moto does the same, so code that forgot to page
fails a test with 1,005 objects instead of failing in production in the month the bucket passes
1,000 results. The paginator follows the tokens for you; lesson 12.5.3's `rebuild` uses it.

Errors come back with AWS's codes, so code can tell them apart:

```text
missing key: NoSuchKey
missing bucket: NoSuchBucket
```

They mean different things to the service. A missing result key is normal (the run is still
waiting), and `S3Store.get_result` turns it into `None`. A missing bucket is a broken deployment, and
must raise. Testing both against moto pins that difference down.

<!-- practice 1 -->

## moto Accepts What AWS Would Refuse, So Validate Before You Call

moto imitates the services' behaviour, not all of their checks. The same program tried four things
AWS documents as refused or as doing work, and moto accepted every one:

```text
upload with a wrong SHA-256 checksum: accepted
state machine whose StartAt names no state: accepted
Batch job submitted without RUN_ID or SNAPSHOT_DIGEST: SUCCEEDED
job name 'run 0002!' with a 30 s timeout: accepted, {'attemptDurationSeconds': 30}
```

What AWS does instead, from its documentation:

- **Checksums.** S3 computes its own checksum of an upload and validates it against the one the
  client sent before storing the object. moto stored the body under a checksum it does not match.
- **State machine definitions.** The Amazon States Language requires `StartAt` to match, exactly,
  the name of one of the states; moto stored a definition whose `StartAt` names none. moto's documentation also says that by default an execution runs none
  of its states and returns static data, which is why lesson 12.5.2 called the failure function by
  hand.
- **Batch jobs.** With `use_docker` off, as this module configures it, moto's documentation says job
  scripts are not executed and are assumed to succeed. A job with no settings at all "succeeded".
- **Batch names and timeouts.** `SubmitJob` allows letters, numbers, hyphens and underscores in a job
  name, starting with a letter or number; `run 0002!` breaks both rules. A job's timeout is at least
  60 seconds. moto accepted both.
- **Permissions.** moto's IAM page says that by default it does not authenticate or authorize
  anything: every call above was made with the key `testing`, which no IAM user owns. A test against
  moto never fails because a role lacks a permission. (`set_initial_no_auth_action_count` turns
  checking on, for the services that support it.)

So a green moto suite proves the code handles AWS's responses, and nothing about whether AWS would
accept its requests. Two habits close most of the gap:

- **Check requests in your own code, before the call**, against the documented rules: job names,
  timeouts, Fargate sizes (lesson 12.5.2), a definition's states. The checks are then tested like any
  other function, and run in production too.
- **Assert on what was sent, not on what moto says happened.** Read the job back with
  `describe_jobs`, as lesson 12.5.2's test does, or capture the request parameters with a botocore
  event hook (`client.meta.events.register("provide-client-params.batch.SubmitJob", ...)`), and
  assert on those. Never assert that a job `SUCCEEDED`: moto would say so for any job.

Permissions are checked another way: by reading the policy (lesson 12.5.5) and, before the first
deployment, by one run in a test account, which this course does not do.

<!-- practice 2 -->

## Summary

- **Fake credentials come first, so no test can sign as anyone.** Set moto's `testing` values in a
  fixture before any client exists; without credentials boto3 refuses to sign.
- **`mock_aws` gives every test a fresh, empty AWS.** Start the mock, then make the client, in that
  order, in fixtures.
- **moto returns AWS's errors and pages, so test them.** 1,000 keys per list call; `NoSuchKey`
  versus `NoSuchBucket`.
- **moto accepts what AWS would refuse, so validate before you call.** It accepted a wrong checksum,
  a broken state machine, an invalid job name and a 30 s timeout, marked an unrunnable job
  `SUCCEEDED`, and checks no permissions.

## Reference

| moto | What it does |
| --- | --- |
| `with mock_aws():` / `@mock_aws` | every AWS service faked in memory, empty at start |
| `mock_aws(config={"batch": {"use_docker": False}})` | Batch jobs not run; assumed to succeed |
| `mock_aws(config={"stepfunctions": {"execute_state_machine": True}})` | moto parses and runs definitions |
| account id `123456789012` | moto's placeholder account |

| What you test | moto supports it? |
| --- | --- |
| response shapes, keys, bodies | yes |
| error codes (`NoSuchKey`, `PreconditionFailed`, `ExecutionAlreadyExists`) | yes, for the calls this module makes |
| list paging at 1,000 keys | yes |
| request validation (names, timeouts, checksums, definitions) | no, in this module's runs |
| IAM permissions | no, unless turned on |
| the job's container actually running | no, with `use_docker` off |

**Further reading:** OR-Tools, the [MathOpt overview](https://developers.google.com/optimization/math_opt)
(the solve these tests store and read back); moto,
[Getting started](https://docs.getmoto.org/en/latest/docs/getting_started.html) (decorator, context
manager, fake-credential fixture, clients created inside the mock),
[Configuration](https://docs.getmoto.org/en/latest/docs/configuration/index.html) (Batch without
Docker), [Step Functions](https://docs.getmoto.org/en/latest/docs/services/stepfunctions.html) and
[IAM-like access control](https://docs.getmoto.org/en/latest/docs/iam.html); AWS Step Functions,
[State machine structure](https://docs.aws.amazon.com/step-functions/latest/dg/statemachine-structure.html)
(`StartAt`); Amazon S3,
[ListObjectsV2](https://docs.aws.amazon.com/AmazonS3/latest/API/API_ListObjectsV2.html) and
[Checking object integrity](https://docs.aws.amazon.com/AmazonS3/latest/userguide/checking-object-integrity.html);
AWS Batch, [SubmitJob](https://docs.aws.amazon.com/batch/latest/APIReference/API_SubmitJob.html) and
[RegisterJobDefinition](https://docs.aws.amazon.com/batch/latest/APIReference/API_RegisterJobDefinition.html);
boto3, [Paginators](https://docs.aws.amazon.com/boto3/latest/guide/paginators.html); pytest,
[How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html) and
[monkeypatch](https://docs.pytest.org/en/stable/how-to/monkeypatch.html).

## Challenges

1. Write a test that fails if any test in the suite creates a boto3 client before `mock_aws` starts.
   (Look at what `boto3.client` returns and where its endpoint points.)
2. Turn on moto's state-machine execution and run a definition made only of `Pass` and `Choice`
   states. Which parts of `solve-run.asl.json` could it run, and which not?
3. Capture the `SubmitJob` parameters with a botocore event hook and assert the job's timeout is at
   least 60 seconds longer than the solver's limit.

## Design Note: Three Layers of Checking

moto is the middle of three layers. Below it, plain unit tests check the pure functions (the
canonical form, the settings, the request checks) with no AWS at all. moto adds the calls: does the
code send the right requests in the right order, and read the responses and errors correctly? Above
it, one run in a real test account checks what only AWS knows: permissions, quotas, networking, the
image actually starting. This course has no account, so it stops at moto, and says so; the habit of
validating requests yourself moves as much as possible of the top layer down into the bottom one.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**moto_safety.py.** A call with no credentials, then calls inside the mock with the fake ones (*Fake
Credentials Come First*). *Try:* Leave out `AWS_DEFAULT_REGION` from the child's environment and its
`region_name`. Predict the error.

**pytest_with_moto.py.** Four tests of the S3 store with credential, mock and store fixtures, run by
pytest (*mock_aws Gives Every Test a Fresh, Empty AWS*). *Try:* Make the `s3` fixture
`scope="module"`. Predict which test fails.

**moto_limits.py.** Paging, error codes, and four requests moto accepted (*moto Returns AWS's Errors
and Pages*, *moto Accepts What AWS Would Refuse*). *Try:* List with `MaxKeys=500`. Predict the
first call's `KeyCount` and the paginator's total.

- Program: [moto_safety.py](src/moto_safety.py)
- Program: [pytest_with_moto.py](src/pytest_with_moto.py)
- Program: [moto_limits.py](src/moto_limits.py)
