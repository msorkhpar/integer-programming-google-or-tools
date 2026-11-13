# Module Agent Brief

You are writing one module of *Integer Programming with Python and Google OR-Tools*. The lead author
gives you a module slug (for example `02-math-toolkit`) and a git worktree. You write that module and
nothing else. Integration happens after you finish: ingest, quiz readers, ship, site build and the
section's learner judge.

## Read First, in This Order

1. `docs/plan/blueprint.md`: the course's purpose and audience, your module's row (lessons, depth,
   time, what each lesson covers) and the definition of done. `docs/plan/curriculum.json` has the
   lesson numbers and titles.
2. `docs/AUTHORING.md`, all six sections. They are the rules, and the checks enforce most of them;
   its section 5 says what went wrong in the pilot and why the rules exist.
3. The finished modules, as templates: `01-optimization-mindset` (section 1 style) and
   `26-multi-period-timing` (modeling style), with their practices under `exercise-src/`.
4. `00-base/`: the GridCap dataset and helpers every module imports. GridCap is fictional. Never
   present it as real data.

## Sources: Read Them Before You Write

These sources come first:

1. **The OR-Tools documentation is the primary source.** It is the most valuable one we have. For
   every OR-Tools topic your module touches, open the matching pages under
   https://developers.google.com/optimization (MathOpt, CP-SAT, the linear solver wrapper, routing,
   assignment, scheduling, bin packing, network flows) and the examples in the OR-Tools GitHub
   repository (github.com/google/or-tools, `ortools/*/samples` and `examples/python`).
   - Teach the API the way those pages do, and check every API claim against them.
   - You may adapt OR-Tools examples (Apache-2.0 code): rework them onto GridCap or keep their own
     setting, run them in the runner, and say where each one came from ("Adapted from the OR-Tools
     example `...`"). Don't copy the documentation's prose; write your own.
2. **The blueprint's resource library** (docs/plan/blueprint.md, "Resource library"): open the
   sources listed for your section.
3. **docs/plan/resource-links.md**: open the ones that match your module's topics (skip the two
   marked low-value).

Every lesson ends its Reference section with a **Further reading** line that cites the sources you
actually opened for it, OR-Tools pages first. Never cite a source you didn't open.

## What You Write

- `<module>/README.md` and one `<module>/README_S.M.L.md` per lesson.
- `<module>/src/*.py`: every program a lesson quotes or links. Code on a page is lifted line for
  line from these programs, and output on a page is printed by them.
- `<module>/tests/`: tests of the module's programs, as in module 26.
- `exercise-src/<module>/<lesson>/`: `plan.json`, two or three code practices per Core or Deep
  lesson, and one quiz. The file layout is in the docstring of `scripts/exercises.py`.

## What You Never Touch

Your worktree has no `corpus.json`, on purpose: the site walks the repository for manifests and
refuses to start if it finds two. Don't restore it. `scripts/exercises.py prove` works without it.


`corpus.json`, `archive/`, `exercises/`, `practice/`, `.studyforge/`, `PROGRESS.md`, `docs/plan/`,
other modules, `00-base/` and `scripts/`. If one of them needs a change, say so in your final report
and the lead author makes it. The same applies to a rule in `docs/AUTHORING.md` that looks wrong.

## Environment

Your worktree is `.scratch/worktrees/<module>` inside the main checkout, so the default sibling paths
the scripts look for are wrong. Set these for every command:

```
MAIN=$(cd "$(git rev-parse --git-common-dir)/.." && pwd)   # the main checkout
export TOOLCHAIN=$MAIN/../code-server-toolchain
export STUDYFORGE=$MAIN/../studyforge
PY=$MAIN/.venv/bin/python3
```

Keep your own state (env files, notes, temp outputs) under your worktree's `.scratch/`, never in
a shared scratchpad: other module agents run at the same time and can overwrite it.

Run every course program in the offline runner image through `scripts/runner.py`, never on the
host. Run StudyForge and the checks with `$PY`.

The runner image is the toolchain's `optimization` profile, declared with the runtimes `node` and
`python` (`code-server-toolchain/runner-optimization:node-python-amd64-45b9b7a7864e`, 2.36 GB; see
`docs/TOOLCHAIN.md`). It carries Python 3.14.7 with the course's pinned wheels, and Node.js 24.21.0 with
the OpenSpec CLI 2.0.0 on `PATH` as `openspec`, telemetry off.

`scripts/runner.py` runs the GPU variant of the runner (HiGHS built with CUDA, and NVIDIA cuOpt) only
when that image is present and Docker reaches a GPU; otherwise the CPU image, with no error. It prints
its choice on stderr; `TOOLCHAIN_VARIANT=cpu` or `=gpu` forces one. Every program and practice must pass
on the CPU image. GPU-only checks use `00-base/gpu.py`: mark a test `@requires_gpu()`, print
`describe()` where a lesson states its device, and run cuOpt with `run_cuopt(script)` (it lives in its
own venv, F69). Never set highspy's `solver="pdlp"` without `gpu_available()` (F71). The GPU
variant needs an NVIDIA GPU and a Docker engine with the NVIDIA container runtime (an engine without
it has no GPU passthrough, F73), so the runner may print `on unix:///var/run/docker.sock`;
`TOOLCHAIN_GPU_DOCKER_HOST` names another engine. GPU results state the device: print `describe()`. On a
machine where the GPU variant is present, every run defaults to it; set `TOOLCHAIN_VARIANT=cpu` to
check a result on the CPU image. The GPU variant builds from the CPU image, so once rebuilt it carries
Node.js and `openspec` too; it is not rebuilt yet, so run anything that needs `node` or `openspec` with
`TOOLCHAIN_VARIANT=cpu`. cuOpt: set `log_to_console` False (its log names the card's UUID,
F77); its concurrent LP method and its MILPs do not repeat bit for bit (F75, F76).

## Checks: Only What Your Change Touches

Run each check on the lesson or module you changed, never on the whole course, and don't rerun a
check whose inputs did not change (AUTHORING section 6):

| You changed | Run |
| --- | --- |
| a lesson's math | `$PY scripts/check_math.py <module>/README_S.M.L.md` |
| a lesson's code, output or programs | `$PY scripts/runner.py python3 scripts/verify_lessons.py <module>` |
| module tests | `$PY scripts/runner.py python3 -m pytest <module>/tests` |
| a practice or quiz | `$PY scripts/check_exercises.py <module>`, then `$PY scripts/exercises.py prove <module> <lesson>` |

`prove` gates code practices. A quiz still needs its independent reader answers
(`quiz/readings.json`); the lead author collects those, so a quiz waiting on readings is expected.

Before you report done, run each check once over the whole module, and only once.

## Rules That Are Easy to Miss

- **Formulation first.** Every model shows its sets, parameters, bounded variables, objective and
  labelled constraints before any code (AUTHORING section 1).
- **No claim about solver behaviour without a program that showed it.** Write the program, run it,
  and quote its output.
- **Cite only sources you opened**, and copy no copyrighted text: paraphrase, and quote no more than
  a short phrase.
- **Define each term where it is first used**, or link the lesson that defines it.
- **Check every number and cross-reference in prose** against the output or the page it names.
- **Personal data.** Never put a real person's name, email, username, hostname or home path in
  any file, commit, output, request or page. Use placeholders such as `Jane Doe` or
  `/path/to/project`. If a program's output shows one (gurobipy's license error does), don't quote
  that output. StudyForge's archive refuses anything shaped like a home path, real or not: write
  a URL's `~name` segment as `%7Ename` (for example `princeton.edu/%7Eerp/`), and never use
  `/home/<anything>` or `/Users/<anything>` even as made-up test data (use `/srv/...`).
- **No narration and no audio.** That is out of scope.
- **Gurobi licenses.** Only a module that runs gurobipy needs one. Set
  `export GUROBI_LICENSE_FILE=$MAIN/.scratch/licenses/gurobi.lic` (your worktree has none, and
  `scripts/runner.py` mounts that file read-only). Never open, read, copy, hash or print it, and
  start every gurobipy environment quiet (lesson 5.3.1's `quiet_env`) with every Gurobi message
  passed through a mask (lesson 5.3.4), because license messages name the user and the host.
  Practices must not need a license: `exercises.py prove` mounts none.

## Quiz Wording

An independent reader tries each question with no page, using only cues in the wording. Before you
finish, check that no key:
- is longer or more specific than the other options;
- repeats a stem word that no other option repeats;
- restates the stem;
- is the only option without an absolute word ("always", "never", "every", "any").

A second reader then checks the page: it must decide the key and clearly rule out every wrong option.
Don't use a wrong option that is half true (one the page's own numbers partly support); pick one the
page contradicts outright, or add the sentence that does, backed by a printed output.

## Finishing

Commit to your worktree branch: one commit per module, with a message saying what the module
teaches, ending with the attribution line the lead author gives you. Never push.

Your final report lists:
- the files you wrote;
- each lesson's practices;
- the last result of each check;
- anything you could not do, and why;
- every change you need outside your module.
