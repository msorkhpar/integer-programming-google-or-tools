# 12.5. Cloud Deployment

Packaging the GridCap service for AWS: a container image that pins the solver and reads its settings
from the environment; AWS Batch on Fargate for the solves, Step Functions to wait for them and catch
failures, and Lambda for the short clean-up; S3 for content-addressed snapshots and write-once
results, with a local SQLite file that indexes the runs; tests against moto, and what moto does not
check; Terraform for the stack; and a GitHub Actions pipeline that tests, builds and deploys.

## What You Run, and What You Only Read

This module is partly read-along, and it says so plainly: **Docker, Terraform and GitHub Actions are
never run in this course.** The Dockerfile, the compose file, the Terraform configuration and the
workflow in `deploy/` were written for you to read; none was built, applied or run, and no output on
these pages comes from them. Running them needs Docker, an AWS account and a GitHub repository,
which the course's offline runner does not have.

What you can run:

- every program in `src/`, in the runner. The ones that call AWS talk to moto, a library that imitates
  S3, Batch, Step Functions and IAM inside the Python process, so no AWS account, credential or
  network is involved;
- the module's tests and every practice, which use moto the same way or work on plain Python data
  (a Dockerfile's text, a parsed workflow, a Terraform plan's JSON);
- the checks the read-along files would face: the practices review a Dockerfile, lint a workflow
  and gate a Terraform plan without running Docker, Actions or Terraform.

What to say about the rest in an interview: be exact about what you have done. "I wrote and
reviewed the Dockerfile, the Terraform and the workflow, and I tested the AWS calls against moto; I
have not deployed this stack to a real account" is a strong answer, because you can then explain
each file line by line and name what moto does not check (lesson 12.5.4 shows a job name and a
timeout moto accepted that AWS Batch refuses). Never claim a deployment you did not run.

## Contents

1. [Containerizing a solver service](README_12.5.1.md)
2. [AWS Batch on Fargate, Step Functions and Lambda: who does what](README_12.5.2.md)
3. [S3 and a local SQLite file for snapshots and results](README_12.5.3.md)
4. [Testing AWS code against moto](README_12.5.4.md)
5. [Terraform for the optimization stack](README_12.5.5.md)
6. [CI/CD with GitHub Actions](README_12.5.6.md)
