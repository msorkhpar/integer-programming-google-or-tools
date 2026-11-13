# Running the course: Integer Programming with Python and Google OR-Tools

This guide is for a learner or a reviewer who runs the course from a checkout of this repository.
[`README.md`](README.md) is the course's curriculum record; this file says how to run it.

## The course

Integer Programming with Python and Google OR-Tools is a self-study course: you read its lessons in
a browser and work its practices in an editor, on your own machine. It takes a software engineer who
writes basic Python from "what is an optimization model?" to a tested, explainable, deployable
capital-planning MILP service.

It has 237 lessons in 57 modules, grouped in 15 sections: Foundations, Linear programming, Integer
programming foundations, Google OR-Tools in depth, Other modeling frameworks and solvers, Formulation
craft, The capital planning domain, Multi-objective optimization, Diagnostics and explainability,
Numerics and determinism, Performance at scale, Engineering the optimization service, Capstone,
Growing real projects and Mock interviews.

It holds 715 practices: 478 to write in code, graded by a real runner, and 237 short quizzes (one
per lesson, 719 questions in all), graded in the page.

Every lesson works on **GridCap**, the capital portfolio of a utility. GridCap is fictional: it
describes no real company.

## What you get

**Lessons.** Each lesson is a page of text and code, with the course contents, an outline of the
page and links to the previous and next lesson. The index shows what you have read and what comes
next, and filters the contents as you type.

**Practices graded by a real runner.** A code practice gives you a statement, starting code and
tests. You write your answer in an editor, and **Submit** runs the practice's tests in a runner that
has no network. The report says whether the main ask is done and how many edge cases pass, and a
practice counts as passed when its tests pass.

**The practice workspace.** Opening a practice fills the window: the statement on the left, the
editor on the right, and a report bar below. **Run** tries your code, **Submit** runs the tests. A
worked solution is one click away when you are stuck.

**Quizzes graded in the page.** Each lesson ends with a short quiz. Choose your answers, press
**Check answers**, and each choice is explained right or wrong. The page grades it.

**Code examples that open in an editor.** A lesson's example expands in place into the editor, with
its source and its test beside the text and a button that runs the test. The editor shows a copy, so
the course's own files stay as they are.

**Reading marks and progress.** Mark a lesson as read and the index counts it. Your marks and quiz
passes are kept in your browser; your practice results are kept on your machine (see
[Where your work is kept](#where-your-work-is-kept)).

## Two ways to use it

The **full course** runs on your machine with Docker, from this checkout. A **read-only preview** of
the lessons on a website is planned but not published yet.

| | Read-only preview | Full course, with Docker |
|---|---|---|
| Set-up | Not published yet | Docker and the images: [Run it locally with Docker](#run-it-locally-with-docker) |
| Lessons, the index and its filter | Not yet | Yes |
| Quizzes, graded in the page | Not yet | Yes |
| Run and Submit, graded by the runner | No | Yes |
| The editor beside the statement | No | Yes |
| Works offline | No | Yes |

## What you need

- Docker: Docker Desktop on Windows or macOS, or Docker Engine with the compose plugin on Linux.
- A current browser.
- To build the images: Python 3 and a checkout of the toolchain repository,
  studyforge-code-server-toolchain, with its `optimization` image profile; and, for the study site,
  the StudyForge library at the version this course pins. The course does not publish images; you
  build them once.
- Room for the images: the runner alone is about 2.4 GB.

Nothing else on your machine: what the practices need (Python 3.14, OR-Tools, HiGHS, SCIP through
MathOpt, Pyomo, PuLP, gurobipy, pandas, pytest, FastAPI, Node.js and the rest) is inside the runner.
The pinned versions are in [`docs/TOOLCHAIN.md`](docs/TOOLCHAIN.md).

Optional:

- **An NVIDIA GPU**, for the GPU checks of module 57 (see [The optional GPU image](#the-optional-gpu-image)).
- **Your own Gurobi licence**, for running the gurobipy lessons' programs (see [Gurobi](#gurobi)).

## Run it locally with Docker

Every command below is one line, run from the root of this checkout unless it says otherwise. Each
runs as printed in PowerShell on Windows and in any POSIX shell; where `python3` is not on a Windows
`PATH`, `py -3` runs the same build line.

### 1. Build the runner and the editor

The course runs in two images built from the toolchain checkout, under the `optimization` profile:

| Image | Repository | Its tag is recorded in |
|---|---|---|
| The runner, where Run and Submit happen | `code-server-toolchain/runner-optimization` | `.studyforge/execution/runner.env` (`STUDYFORGE_RUNNER_IMAGE`) |
| The editor (code-server), opened inside each practice | `code-server-toolchain/editor-optimization` | `.studyforge/execution/editor.env` (`EDITOR_IMAGE`) |

The profile layers on the toolchain's shared base images. In the toolchain checkout, build the base
runner, then the base editor:

```
python3 docker/minimal/build.py --runtimes node,python
python3 docker/editor/build.py --runtimes node,python
```

Then build the `optimization` profile's runner and editor on those bases, as the toolchain's own
profile instructions say.

A tag is not a name you choose: the toolchain computes it from the build's inputs and your platform
(`linux/amd64` or `linux/arm64`). Ask the toolchain for each one, in its checkout:

```
python3 docker/profile_packages/package_build.py --profile optimization --image runner --runtimes node,python --print-tag --platform <platform>
python3 docker/profile_packages/package_build.py --profile optimization --image editor --runtimes node,python --print-tag --platform <platform>
```

The tags in `runner.env` and `editor.env` were printed this way for an amd64 machine. If yours
prints a different tag (another platform, or a newer toolchain), the files must name it: they are
generated by StudyForge's execution onboarding, which re-records them, so regenerate them rather
than editing them by hand.

### 2. Stage the study site

The study site's image (`studyforge-site`, named in `.studyforge/execution/site.env`) is built from
the StudyForge library this course pins: version 0.1.0, at the commit recorded in
[`.studyforge/pin.json`](.studyforge/pin.json). Its build context needs a copy of that library,
which is not committed. With the StudyForge wheel built from that commit installed in your Python,
stage it from the root of this checkout (a POSIX shell line):

```sh
python3 -c "from pathlib import Path; from studyforge.skills.execution.siteimage import stage_site; print(stage_site(Path('.')).tag)"
```

It refuses a library whose version or commit differs from the pin. It copies the library into
`.studyforge/execution/site/library/` (ignored by git) and prints the image's tag, which is computed
from those bytes: with the pinned library it is the one already in `site.env`, so the file does not
change.

### 3. Build the study site and bring it up

From the root of this checkout, build the study site's image:

```
docker compose --env-file .studyforge/execution/runner.env --env-file .studyforge/execution/editor.env --env-file .studyforge/execution/instance.env --env-file .studyforge/execution/site.env -f .studyforge/execution/compose.yaml build site
```

Then start the study site, the editor and the runner together:

```
docker compose --env-file .studyforge/execution/runner.env --env-file .studyforge/execution/editor.env --env-file .studyforge/execution/instance.env --env-file .studyforge/execution/site.env -f .studyforge/execution/compose.yaml up -d --wait
```

The first `up` builds the site's image too (once it is staged), if you skipped the build step. A preflight check runs
first and refuses a setting that cannot work, by its name, before anything starts.

Open http://127.0.0.1:8765/ in your browser.

To see what is running, use the same `--env-file` and `-f` options with `ps`. Use them with every
compose command for this course.

### Node.js and the OpenSpec CLI

The runner carries Node.js 24.21.0 and the OpenSpec CLI 2.0.0 (`openspec` on the `PATH`), for
project 14.4, Spec-Driven Development with OpenSpec. OpenSpec's telemetry is off in the image
(`DO_NOT_TRACK=1`, `OPENSPEC_TELEMETRY=0`), and the runner has no network anyway.

### The optional GPU image

Module 57 (lesson group 11.4, GPU Acceleration) runs on the CPU image: every program, test and
practice of the module passes there, and its GPU-only checks skip themselves on a CPU. The study
site's runner is always the CPU image.

The GPU image, `code-server-toolchain/runner-optimization-gpu`, is optional. It is the profile's
runner plus HiGHS built with CUDA and NVIDIA cuOpt, and it needs an NVIDIA GPU and the NVIDIA
container runtime. It is used from a terminal (next section): `scripts/runner.py` picks it only when
the image is present and Docker reaches a GPU, and otherwise runs the CPU image with no error.
`TOOLCHAIN_VARIANT=cpu` forces the CPU image. [`docs/TOOLCHAIN.md`](docs/TOOLCHAIN.md) notes that
the GPU image does not carry Node.js and OpenSpec until it is rebuilt from the current profile; until
then, run anything that needs `node` or `openspec` with `TOOLCHAIN_VARIANT=cpu`.

### Running the examples from a terminal

`scripts/runner.py` runs a command inside the runner image, offline, with this checkout mounted. For
example, the GridCap base library's tests:

```sh
python3 scripts/runner.py python3 -m pytest 00-base
```

It asks the toolchain checkout for the image's tag. It looks for that checkout beside this one
(`../code-server-toolchain`); set `TOOLCHAIN=/path/to/code-server-toolchain` to point elsewhere, or
set `RUNNER_IMAGE` to the tag in `.studyforge/execution/runner.env` to skip the toolchain entirely.
It prints the image it chose on stderr.

### Gurobi

No Gurobi licence is in any image: gurobipy's bundled licence file is removed from the runner. The
practices of the gurobipy module (5.3) need none. To run the module's lesson programs, use your own
licence file, which stays on your machine:

```sh
GUROBI_LICENSE_FILE=/path/to/gurobi.lic python3 scripts/runner.py python3 -m pytest 21-gurobipy
```

When `GUROBI_LICENSE_FILE` names a file that exists, `scripts/runner.py` mounts it read-only in the
container at `/licenses/gurobi.lic` and sets `GRB_LICENSE_FILE` to that path. The file is never
copied into an image or into this checkout. Without a licence, the module's programs stop with
Gurobi error 10009 and their tests skip themselves with that reason. Lesson 5.3.4 explains the kinds
of licence and which of them work in an offline container.

The study site's compose stack in this checkout mounts no licence.

## The ports

| What | Where |
|---|---|
| The study site | http://127.0.0.1:8765/ |
| The editor, which the site opens inside each practice | http://127.0.0.1:8443/ |

Both listen on this machine only (127.0.0.1). The editor has no password, because that loopback bind
is its access control: do not widen it.

[`.studyforge/execution/instance.env`](.studyforge/execution/instance.env) is the one place a port
is set, and it is yours to edit: no regeneration writes over it. To use other ports, change
`STUDYFORGE_SITE_PORT` and `STUDYFORGE_EDITOR_PORT` there, then run the `up` command again. The site
tells each page the editor's new address. The same file names the compose project
(`STUDYFORGE_PROJECT`) and the containers, so a second checkout on the same machine can set its own
and run beside this one.

## Where your work is kept

- **Your practice files** live in `practice/`, in this checkout: the editor opens them there, and
  Submit runs the tests on them.
- **Your practice results** (what you ran and passed) are written to
  `.studyforge/progress/progress.json` in this checkout. That directory ignores itself, so your
  results never reach a commit.
- **The code examples' working copy** is `.studyforge/execution/code`: the editor and the runner use
  this copy, so a test run never writes into the course's own files. Only its ignore file is
  committed.
- **The editor's settings and data** live in two Docker volumes, `editor-config` and `editor-data`.
- **Your reading marks and quiz passes** are kept in your browser.

All of these survive a restart. `practice/` and `.studyforge/execution/code` must exist before the
first `up` (both are in the checkout); if Docker had to create them, they would be owned by root and
the containers could not write them.

## The exercises

`exercise-src/` holds the sources each practice and quiz is authored from: statement, starting code,
reference solution, tests and quiz. `scripts/exercises.py` builds them into `exercises/`, the
bundles the site reads. `practice/` holds your working copy of each practice: the files you edit and
submit live there, and `exercises/` is only read.

## Stop it

```
docker compose --env-file .studyforge/execution/runner.env --env-file .studyforge/execution/editor.env --env-file .studyforge/execution/instance.env --env-file .studyforge/execution/site.env -f .studyforge/execution/compose.yaml down
```

`down` stops and removes the containers and keeps your work. Adding `-v` (`down -v`) also deletes
the editor's two volumes, `editor-config` and `editor-data`, so its settings and data are lost. Your files in `practice/` and your results in `.studyforge/progress/` are in the checkout,
not in a volume, so neither command deletes them.

## The online preview

A read-only preview of the lessons is not published yet.

## Licence

The course is released under the MIT licence: see [`LICENSE`](LICENSE). Examples adapted from
the OR-Tools samples (Apache-2.0) are marked with where they came from.

## How this course was built

The course was built with StudyForge, which reads the lessons from this repository and serves them
with their practices. Every program a lesson shows was run in the course's runner image, and the
lesson shows the output it printed. Each practice's reference solution passes its tests in the
runner, and the tests were checked against planted mistakes. Each lesson's quiz was checked by
separate quiz readers, and each section was read by learner judges at the level the course starts
from.
