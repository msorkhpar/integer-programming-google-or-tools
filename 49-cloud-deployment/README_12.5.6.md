# 12.5.6 CI/CD With GitHub Actions

Everything is now in place to deploy GridCap's service: an image (lesson 12.5.1), the Batch and
Step Functions design (lesson 12.5.2), the store and index (lesson 12.5.3), a moto test suite (lesson
12.5.4), and the Terraform (lesson 12.5.5). Done by hand, a release is a dozen commands typed in the
right order by whoever has the AWS keys, and the day someone skips the tests or applies from a stale
branch, the plan of record runs on code nobody reviewed. **CI/CD** (continuous integration and
delivery) moves those commands into a file in the repository that a service runs on every change:
the tests on every pull request, and the build and deploy on every merge to `main`. This lesson reads
GridCap's workflow for **GitHub Actions**, GitHub's CI service, and checks it with a program.
(GridCap is fictional; no number in it is real.)

**This lesson is read-along for its workflow.** The course does not run GitHub Actions: the file
lives at `deploy/github-workflows/ci.yml`, not under `.github/workflows/`, so no service runs it.
`workflow_review.py` parses it and reasons about it, and its output is printed. No model is built or
changed here.

## A Workflow Is Jobs, a Job Is Steps, and needs Orders the Jobs

A **workflow** is a YAML file. `on` names the events that start it; `jobs` holds the **jobs**, each
run on a fresh machine (a **runner**) as a list of **steps**: a shell command (`run`) or a reusable
**action** (`uses`). Jobs run in parallel unless one **needs** another. The head of GridCap's
workflow:

```yaml
name: ci

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read
```

It starts on every pull request, and on every push to `main` (a merge). Its three jobs are `test`,
`image` (needs `test`) and `deploy` (needs `test` and `image`), and the last two carry
`if: github.event_name == 'push'`. GitHub's workflow syntax reference states the rule that decides
what runs: if a job's `if` is false it is skipped, and if a job it needs fails or is skipped, it is
skipped too, all the way down the chain, unless its `if` uses a function such as `always()`.
`workflow_review.py` applies that rule to the file for each event:

```python
def runs_on(event: str) -> dict[str, str]:
    """Each job's fate for one event: an `if` on the event name, then skipped if any need did not run."""
    fate: dict[str, str] = {}
    for name, job in jobs.items():                       # the file lists every job after its needs
        condition = job.get("if", "")
        wanted = re.search(r"github\.event_name == '(\w+)'", condition)
        if any(fate[n] != "runs" for n in needs(job)) or (wanted and wanted.group(1) != event):
            fate[name] = "skipped"
        else:
            fate[name] = "runs"
    return fate
```

```text
pull_request  {'test': 'runs', 'image': 'skipped', 'deploy': 'skipped'}
push          {'test': 'runs', 'image': 'runs', 'deploy': 'runs'}
```

A pull request runs only the tests. A merge runs all three, in order, and a failing test stops the
build and the deploy, because they need it. (The program reads only this file's simple `if`s; it is a
model of the rule, not of GitHub's expression language.)

One trap when a program reads a workflow. PyYAML follows YAML 1.1, in which a bare `on` is a
boolean, so the key comes back as `True`:

```text
top-level keys: ['name', True, 'permissions', 'env', 'jobs']
```

GitHub reads the file its own way, so the workflow is fine; a script that looks up `flow["on"]` gets
a `KeyError`. Quote it (`"on":`) or look up `True` when you parse workflows yourself.

## Tests Run on Every Change, Against moto, With No Credentials

The `test` job is the course's own habit, moved to a server:

```yaml
  test:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@0000000000000000000000000000000000000000  # v5
      - uses: actions/setup-python@0000000000000000000000000000000000000000  # v6
        with:
          python-version: "3.14"
      - run: pip install -r requirements.txt
      - run: python -m pytest       # moto only: this job has no AWS credentials at all
```

The suite of lesson 12.5.4 needs no AWS, so this job is given none: it has no role and the workflow
references no secrets. A test that escaped moto would fail with `NoCredentialsError` (lesson
12.5.4's first output), not reach an account. The job pins the runner image (`ubuntu-24.04`) and the
Python version, for the reason lesson 12.5.1 pinned the solver: a result that changes when the
machine changes is not a test.

## CI Gets AWS Access From OIDC, Never From Stored Keys

The `image` and `deploy` jobs must act in AWS. The old way stores an access key as a repository
secret; it never expires, and anyone who can change a workflow can print it. GitHub's documentation
describes the replacement, **OpenID Connect (OIDC)**: the job asks GitHub for a short-lived signed
token that says which repository, branch and environment it runs for, and AWS exchanges it for
temporary credentials of a role whose trust policy accepts exactly those claims (the audience
`sts.amazonaws.com`, and a subject naming the repository). Nothing long-lived exists to steal. In
the workflow it takes two things:

```yaml
    permissions:
      contents: read
      id-token: write
```

```yaml
      - uses: aws-actions/configure-aws-credentials@0000000000000000000000000000000000000000  # v5
        with:
          role-to-assume: arn:aws:iam::123456789012:role/gridcap-ci-push
          aws-region: us-east-1
```

`id-token: write` lets the job request the token; `configure-aws-credentials` trades it for the role's
credentials. Each job assumes its own role: `gridcap-ci-push` may push images to the registry,
`gridcap-ci-deploy` may apply Terraform. The program confirms no secret is referenced anywhere:

```text
secrets referenced: []
```

## Pin Every Action to a Commit and Give the Token Least Privilege

An action is someone else's code running with your job's permissions. A tag such as `@v5` can be
moved by whoever controls the action's repository, so the next run can execute different code.
GitHub's security-hardening guide recommends pinning each action to a full-length commit SHA, which
cannot move, with the version in a comment for people. The SHAs in this file are all zeros:
placeholders, because the course cannot look up and verify each release's commit. A real workflow
replaces each with the commit of the release its comment names.

The same guide says to give the workflow's `GITHUB_TOKEN` (the credential every job gets for GitHub
itself) the least access it needs. The workflow sets `contents: read` at the top, and only the two
jobs that talk to AWS add `id-token: write`. The program prints each job's needs, permissions, pins
and environment:

```text
test    needs -                 permissions {'contents': 'read'}, every action SHA-pinned: True, environment: -
image   needs ['test']          permissions {'contents': 'read', 'id-token': 'write'}, every action SHA-pinned: True, environment: -
deploy  needs ['test', 'image'] permissions {'contents': 'read', 'id-token': 'write'}, every action SHA-pinned: True, environment: production
```

The workflow syntax reference says a `permissions` block sets every scope it does not name to `none`,
and that the job's block is applied after the workflow's. So `image` and `deploy` repeat
`contents: read`, which checking out the code needs; without it they would have `id-token` alone.

<!-- practice 1 -->

## Deploy Builds One Image per Commit, Then Plans, Checks and Applies Behind an Environment

The `image` job tags each image with the commit that built it, `${{ github.sha }}`, and pushes it to
the immutable repository of lesson 12.5.5:

```yaml
      - run: docker build -t "$REGISTRY/gridcap-solver:${{ github.sha }}" .
      - run: docker push "$REGISTRY/gridcap-solver:${{ github.sha }}"
```

Every image is then traceable to a commit, and every run's container to its image. A planner's
question "which code solved this?" has an answer: the job definition names the tag, and the tag is
the commit.

The `deploy` job runs lesson 12.5.5's loop, with its check between plan and apply:

```yaml
      - run: terraform -chdir=deploy/terraform show -json tfplan > plan.json
      - run: python plan_guard.py plan.json      # the plan gate: refuses a plan that destroys history
      - run: terraform -chdir=deploy/terraform apply -input=false tfplan
```

`plan_guard.py` is the service repository's copy of lesson 12.5.5's rule, exiting non-zero on a
blocked plan. A non-zero exit fails the step, the job stops, and `apply` never runs. The plan is
made with the new image's tag as `-var "image=..."`, so the job definition's revision points at
exactly the image this run built.

The job also names an **environment**, `production`. In GitHub, an environment can carry
protection rules, such as required reviewers (up to six; one approval is enough); the workflow
syntax reference says every protection rule must pass before a job that references the environment
is sent to a runner. So a merge to `main` runs the tests and builds the image by itself, and the
apply waits for a person to approve it.

<!-- practice 2 -->

## Summary

- **A workflow is jobs, a job is steps, and `needs` orders the jobs.** A job whose need failed or was
  skipped is skipped; pull requests run the tests only. PyYAML reads `on` as `True`.
- **Tests run on every change, against moto, with no credentials.**
- **CI gets AWS access from OIDC, never from stored keys.** `id-token: write` and a role per job.
- **Pin every action to a commit and give the token least privilege.** A `permissions` block sets
  every scope it does not name to `none`.
- **Deploy builds one image per commit, then plans, checks and applies behind an environment.**

## Reference

| Workflow key | What it does |
| --- | --- |
| `on: {pull_request, push: {branches: [main]}}` | the events that start the workflow |
| `jobs.<id>.needs: [a, b]` | run after `a` and `b` succeed; skipped if either fails or is skipped |
| `jobs.<id>.if: <expression>` | skip the job when false; `always()` runs it whatever its needs did |
| `permissions: {contents: read, id-token: write}` | the `GITHUB_TOKEN`'s access; unnamed scopes are `none` |
| `jobs.<id>.environment: production` | protection rules (reviewers) pass before the job runs |
| `uses: owner/action@<40-hex SHA>  # vN` | an action pinned to a commit |

**Further reading:** OR-Tools, [Installing OR-Tools for Python](https://developers.google.com/optimization/install/python)
(what CI's `pip install` fetches); GitHub, [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions)
(`on`, `needs` and skipped jobs, `if`, `permissions`, `environment`),
[Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
(SHA pinning, least-privilege `GITHUB_TOKEN`, OIDC over stored secrets),
[Configuring OpenID Connect in Amazon Web Services](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
(`id-token: write`, `role-to-assume`, the trust policy's `aud` and `sub`) and
[Managing environments for deployment](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-deployments/managing-environments-for-deployment)
(required reviewers); Terraform, [JSON output format](https://developer.hashicorp.com/terraform/internals/json-format).

## Challenges

1. Add a `plan` job that runs on pull requests and prints the plan for reviewers, without being able
   to apply it. Which role does it assume, and what may that role do?
2. A workflow step runs `pip install -r requirements.txt`. What could still differ between two runs
   a month apart, and what would make them identical?
3. Make the `deploy` job also run when `image` was skipped because the image for this commit already
   exists. Write the `if`, and say what you must check first.

## Design Note: The Pipeline Is Part of the Model's Trust

Section 10 made the solve repeatable and section 12 made it testable. CI is where both are
enforced: the determinism and golden tests of lessons 12.3.3 and 12.3.4 run on every change, no code reaches the
Batch job definition without passing them, and every result in S3 names a snapshot, every run an
image, every image a commit. When a regulator asks how a plan was produced, the chain from the plan
of record to the commit is written down by the pipeline, not reconstructed from memory.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**workflow_review.py.** Parses the workflow, works out which jobs run for each event, and prints each
job's needs, permissions, pins and environment (all sections). *Try:* Replace one SHA in `ci.yml`
with `v5`. Predict which job's line changes.

- Program: [workflow_review.py](src/workflow_review.py)
