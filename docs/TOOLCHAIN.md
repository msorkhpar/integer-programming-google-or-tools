# Toolchain

The course's examples, tests and practices run in the `optimization` image profile of
studyforge-code-server-toolchain. The profile layers on the shared `python` and `node` bases, so no
other course's image carries these packages. The course declares both runtimes: `corpus.json` has
`"runtimes": ["node", "python"]`, and `scripts/runner.py` and `scripts/exercises.py` pass
`--runtimes node,python` to the toolchain, which refuses a set without `node` for this profile.

| | |
| --- | --- |
| Toolchain branch | `feat/optimization-profile` (local, not pushed) |
| Toolchain commit | `e7d6d88` |
| Profile | `optimization` (`profiles/optimization.json`) |
| Runtimes | `node`, `python` |
| Runner tag | `code-server-toolchain/runner-optimization:node-python-amd64-45b9b7a7864e` (2.36 GB) |
| Base runner | `code-server-toolchain/runner:node-python-amd64-f8f1db0be48a` (Python 3.14.7, Node.js 24.21.0) |

Ask the toolchain for the tag rather than copying it:

```sh
python3 docker/profile_packages/package_build.py --profile optimization --image runner \
  --runtimes node,python --print-tag
```

### Optional GPU variant

`optimization-gpu` (runner only) is the profile's runner plus HiGHS built with CUDA and NVIDIA cuOpt. It
needs an NVIDIA GPU and a Docker engine with the NVIDIA container runtime. `scripts/runner.py` picks it
only when its image is present and Docker reaches a GPU, and `TOOLCHAIN_VARIANT=cpu` forces the CPU
image. The variant builds from the profile's own image, so once it is rebuilt it carries Node.js and the
OpenSpec CLI too, under the tag `runner-optimization-gpu:node-python-amd64-<hash>`. **It is not rebuilt
yet**: the last GPU image built is the older `python-amd64` one, without Node.js, so run anything that
needs `node` or `openspec` with `TOOLCHAIN_VARIANT=cpu` until it is.

## Pinned versions

| Package | Version | Note |
| --- | --- | --- |
| ortools | 9.15.6755 | MathOpt, CP-SAT, GLOP, PDLP; bundles HiGHS and SCIP for MathOpt |
| highspy | 1.14.0 | held: 1.15.x and OR-Tools 9.15 cannot load in one process |
| gurobipy | 13.0.3 | **no license in any image**: the wheel's bundled license file is removed; a learner mounts their own read-only and sets `GRB_LICENSE_FILE` |
| pyomo | 6.10.1 | solves with HiGHS through highspy |
| pulp | 3.3.2 | held: last line that bundles CBC and keeps the classic API |
| numpy / scipy / pandas | 2.5.4 / 1.18.1 / 3.1.0 | |
| numpy-financial | 1.1.0 | |
| matplotlib | 3.11.2 | |
| pydantic | 2.14.1 | |
| hypothesis | 6.170.13 | |
| fastapi / httpx | 0.162.0 / 0.28.1 | |
| boto3 / moto | 1.43.121 / 5.2.5 | moto with the `s3` extra |
| pytest | 9.1.1 | from the base image |
| Node.js | 24.21.0 | from the shared `node` base (the official tarball, checked by sha256) |
| @fission-ai/openspec | 2.0.0 | on `PATH` as `openspec`, installed offline from a lockfile; telemetry off (`DO_NOT_TRACK=1`, `OPENSPEC_TELEMETRY=0`) |

Locally, `.venv` holds the same pins (Python 3.14.4), installed from the same hashed requirements file.

## Rules for running code

- Run examples, tests and gates **in the runner image**, not on the host: a host run can print the
  machine's user and host name (Gurobi's "No Gurobi license found (user ..., host ...)" does), and
  that must never reach a lesson, a log in the repository or a commit.
- Scripts never choose a Docker engine or context: they use whatever `docker` the person running
  them has selected.
- Gurobi lessons and practices read the license from `GRB_LICENSE_FILE`, mounted read-only at run
  time. No license file is ever committed, baked into an image or published.
