# 5.3.4 Licenses: Size-Limited, Academic, and Cloud/Container (WLS)

GridCap's scenario service (section 12) will run its solves as container jobs on AWS. The partner
from lesson 5.3.1 suggests Gurobi for them, and the team lead asks three plain questions before
anyone writes a line: which license would those containers use, what happens on a laptop or a
build server that has none, and how do we keep license details out of logs and pages? Gurobi is
commercial software. Unlike HiGHS, SCIP and CP-SAT, which ship inside OR-Tools, it runs only with a
license, and what that license allows (model size, machines, containers, who may use it) decides
where a Gurobi model can run at all. GridCap is a fictional utility.

**To run this module's programs you need your own Gurobi license.** The course does not supply one,
and no license is stored in the course's images, files or pages. The last section shows how to give
the course's runner yours. The practices of this module need none: they work with gurobipy's
constants and with plain data.

## gurobipy Needs a License Before It Builds Anything

A Gurobi environment reads the license when it starts (lesson 5.3.1), and every model lives in an
environment, so without a license nothing can be built. `license_errors.py` shows what a program
then sees. It runs each case in a child process with its own environment variables, so the result
does not depend on the license of the machine it runs on: first with no license anywhere, then with
`GRB_LICENSE_FILE` pointing at a file that does not exist.

```python
try:
    env = gp.Env(empty=True)
    env.setParam("OutputFlag", 0)
    for name, value in params.items():
        env.setParam(name, value)
    env.start()
    print("started")
except gp.GurobiError as error:
    print("GurobiError", error.errno, mask(str(error)))
```

```text
no license anywhere:
  GurobiError 10009 No Gurobi license found (user <user>, host <host>, hostid <hostid>, cores <n>)
GRB_LICENSE_FILE to a missing file:
  GurobiError 10009 Unable to open Gurobi license file '/licenses/missing.lic'
```

Both are error 10009, a license error, raised by `start()` before any model exists. The first
message names the machine: the user running the program, the host's name, a host id and the number
of cores. **The output above is masked**: `mask` (next-but-one section) replaced each of those with
a placeholder before printing. The raw message carries real values, and a program that prints it,
logs it or returns it from an API hands them to whoever reads that output. Every Gurobi message in
this course goes through `mask` first.

Where Gurobi looks, according to its support article on placing the license file: on Linux, in
`/opt/gurobi` and in the user's home directory; on Windows `C:\gurobi`, on macOS `/Library/gurobi`,
each also with the home directory. A file anywhere else is found only through the environment
variable **`GRB_LICENSE_FILE`**, which must name the file itself, not its folder. The second case
shows the message when the variable names a file that is not there: it names the file Gurobi could
not open.

## Four Kinds of License, and Where Each Can Run

| License | Who gets it | Limits | Containers |
| --- | --- | --- | --- |
| **Size-limited** (restricted) | anyone: it comes inside the `gurobipy` pip and conda packages | models up to 2,000 variables and 2,000 linear constraints (200 variables if there are quadratic terms) | the file travels with the package; this course removes it from its images (last section) |
| **Academic named-user** | students, faculty and staff of a degree-granting institution, for research, teaching or coursework | full size; one user on one machine; renewed yearly | no: the academic licensing article says it cannot be used in containers |
| **Academic WLS** (Web License Service) | the same people | full size; several machines, containers included; needs an Internet connection while jobs run; 90 days, renewable | yes |
| **Commercial** | bought from Gurobi | as purchased | the Docker Hub page for Gurobi's own image names WLS, Compute Server, Gurobi Cloud and a token server as the ways in, and says node and academic licenses do not work in containers |

The first row is what `pip install gurobipy` gives on your own computer. Its limits are checked when
the model is solved, as the next section shows.

The **Web License Service** is the license for machines that come and go. Instead of a file tied to
one machine, a program holds an API key, three values from Gurobi's Web License Manager: an access
id (`WLSAccessID`), a secret (`WLSSecret`) and a license id (`LicenseID`, a number). When the
environment starts, Gurobi exchanges them over the Internet for a short-lived token (the `WLSTokenDuration`
parameter caps its life at 5 to 60 minutes) and renews it as needed. A container on AWS Batch or
Fargate is exactly such a machine, so running there does not remove the licensing question: it
answers it with WLS (or a license server the containers can reach), and the container needs outbound
Internet access to Gurobi's servers.

## The Size-Limited License Stops at 2,000 Variables or 2,000 Rows

The course's runner, where this page's outputs were produced, has the size-limited license. Its
limit, measured at both edges and on three GridCap timing models:

```python
for n in (2000, 2001):
    m = gp.Model(f"{n} variables", env=env)
    x = m.addVars(n, ub=1.0, name="x")
    m.setObjective(x.sum(), GRB.MAXIMIZE)
    m.update()
    print(f"{n:,} variables, {m.NumConstrs} rows -> {try_solve(m)}")
```

```text
2,000 variables, 0 rows -> OPTIMAL
2,001 variables, 0 rows -> GurobiError 10010: Model too large for size-limited license; visit https://gurobi.com/unrestricted for more information
1 variable, 2,001 rows -> GurobiError 10010: Model too large for size-limited license; visit https://gurobi.com/unrestricted for more information
GridCap small timing model: 80 variables, 49 rows -> OPTIMAL
GridCap medium timing model: 887 variables, 469 rows -> OPTIMAL
GridCap large timing model: 21,843 variables, 11,467 rows -> GurobiError 10010: Model too large for size-limited license; visit https://gurobi.com/unrestricted for more information
```

The limits are exactly 2,000: one more variable, or one more row, and `optimize()` raises
`GurobiError` 10010. Building the model was allowed; the check came at the solve. GridCap small and
medium fit, and every model in this module is small. GridCap large, 10,000 projects, is ten times
over, and with this license it cannot be solved at all; with an academic or commercial license the
same program solves it (within the 60-second time limit `try_solve` sets). A team planning on the
size-limited license should count before it builds: `NumVars` and `NumConstrs` after an `update()`
tell, without solving, whether a model will be refused.

## A Container Gets Its License at Run Time, Never in the Image

A container image is copied, cached and shared. A license file or WLS key built into it goes
everywhere the image goes, and the Docker Hub page for Gurobi's own image advises against baking
the license into an image. The rule is the same for both kinds of license: the image holds code,
and the license arrives when the container starts.

- **A license file** is mounted read-only into the container and named by `GRB_LICENSE_FILE`
  (Gurobi's Kubernetes example mounts it from a secret and sets that variable).
- **A WLS key** is passed in as environment variables or secrets, and the program hands it to
  `gp.Env(params=...)`. Gurobi's support article on WLS shows the three parameters given that way,
  with `LICENSEID` as a number and the other two as strings.

`licensed_env.py` is one function for both. It reads the process's environment variables (here
named after Gurobi's parameters) and returns the parameters for `gp.Env`:

```python
def env_params(environ: dict[str, str]) -> dict:
    """Parameters for gp.Env(params=...): quiet always, plus a complete WLS key if one is given."""
    params: dict = {"OutputFlag": 0}
    present = [name for name in WLS if environ.get(name)]
    if len(present) == len(WLS):
        params.update(WLSACCESSID=environ["WLSACCESSID"], WLSSECRET=environ["WLSSECRET"],
                      LICENSEID=int(environ["LICENSEID"]))
    elif present:
        missing = ", ".join(name for name in WLS if name not in present)
        raise ValueError(f"incomplete WLS key: {missing} not set")
    return params
```

```python
def redacted(params: dict) -> dict:
    """The parameters with every license value replaced by '<set>'."""
    return {k: ("<set>" if k in WLS else v) for k, v in params.items()}


def open_env(environ: dict[str, str]) -> gp.Env:
    """A started, quiet environment from the deployment's license (raises GurobiError if there is none)."""
    return gp.Env(params=env_params(environ))
```

With no WLS variables it adds nothing, and Gurobi finds the license file itself through
`GRB_LICENSE_FILE` or its default places. A half-given key is refused before Gurobi sees it, with a
message that names the missing variables and none of the values. `OutputFlag=0` goes in the same
dictionary, so the banner is never printed. The demo uses placeholder values, all zeros and ones,
and starts no environment, so it contacts nothing:

```text
course runner, license file mounted: {'OutputFlag': 0}
container with a WLS key           : {'OutputFlag': 0, 'WLSACCESSID': '<set>', 'WLSSECRET': '<set>', 'LICENSEID': '<set>'}
container with half a WLS key      : refused, incomplete WLS key: WLSSECRET, LICENSEID not set
```

`redacted` is the only form in which the parameters are ever printed. A program that logs its
configuration at start-up (a good habit, lesson 10.2.4) logs this one.

<!-- practice 1 -->

## Gurobi's Messages Can Name You; Mask Them

Two kinds of Gurobi output carry personal or license data. The **license banner** a default
environment prints names the license, and can name its holder. The **license errors** name the
user and the host, as the first section showed. Neither belongs in a program's output, a service's logs, a ticket or a lesson. The first is
handled by `quiet_env` and `OutputFlag=0`; the second needs a mask, applied to every message before
it is printed or stored. `grb.py`'s:

```python
MASKS = [
    (re.compile(r"\buser [^,)]*"), "user <user>"),
    (re.compile(r"\bhost [^,)]*"), "host <host>"),
    (re.compile(r"\bhostid [^,)]*"), "hostid <hostid>"),
    (re.compile(r"\bcores \d+"), "cores <n>"),
    (re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+"), "<email>"),
    (re.compile(r"(?i)(license ?id\D{0,12})\d+"), r"\1<id>"),
]


def mask(text: str) -> str:
    """The text with every user, host, host id, core count, e-mail and license id replaced by a placeholder."""
    for pattern, placeholder in MASKS:
        text = pattern.sub(placeholder, text)
    return text
```

Each pattern replaces a value by a placeholder and keeps the words around it, so the message still
says what went wrong. The `*` after `[^,)]` matters: in the course's runner the user name is empty
(`user , host ...`), and a `+` would leave that line unmasked and the next field with it. The
module's tests feed `mask` a message with a made-up user, host, address and license id, and check
that none of them survives.

<!-- practice 2 -->

## Running This Module's Programs in the Course

The course's runner image carries gurobipy 13.0.3 with its bundled license file removed: no
license is baked into any image. To run the programs of this module on the course site, give the
runner your own license file:

1. Get a license file: the size-limited file that `pip install gurobipy` puts inside the installed
   package (`gurobipy/.libs/gurobi.lic`), or one your organization provides for containers.
2. Set `GUROBI_LICENSE_FILE` in the course's `course.env` to that file's path on your computer.
3. The runner then mounts it read-only at `/licenses/gurobi.lic` and sets `GRB_LICENSE_FILE` to that
   path. The file is never copied into the image or the course's folder.

Without it, every program of this module stops at `quiet_env()` with error 10009, as in the first
section, and the module's tests skip themselves with that reason. The size-limited license runs
every program here; the lesson outputs were produced with it. It is also, in practice, the license
the course's runner can use: an academic named-user license does not work in containers (the
academic licensing article says so), and a WLS license needs the container to reach Gurobi's
servers, which the runner, offline by design, cannot do. Academic and WLS licenses are for your own
machine or your own deployments, as the sections above describe.

What about MathOpt with `SolverType.GUROBI`? In the course's runner it fails (lesson 4.2.3): OR-Tools
9.15 cannot load the Gurobi 13 library that comes with gurobipy. A license
does not change that; the version mismatch does. That is why this module teaches Gurobi through
gurobipy.

## Summary

- **gurobipy needs a license before it builds anything.** `Env.start()` raises `GurobiError` 10009
  without one; the message names the user and host, so it is masked before it is shown.
  `GRB_LICENSE_FILE` names the file; otherwise Gurobi looks in its default places.
- **Four kinds of license, and where each can run.** Size-limited (pip), academic named-user (one
  machine, no containers), academic WLS (containers, online), commercial.
- **The size-limited license stops at 2,000 variables or 2,000 rows**, at `optimize()`, with
  error 10010. GridCap small and medium fit; large does not.
- **A container gets its license at run time, never in the image**: a file mounted read-only, or a
  WLS key passed to `gp.Env(params=...)`, logged only redacted.
- **Gurobi's messages can name you; mask them**: users, hosts, ids, addresses, before anything is
  printed or stored.

## Reference

| Task | Code or setting |
| --- | --- |
| name the license file | `GRB_LICENSE_FILE=/path/to/gurobi.lic` (the file, not its folder) |
| a WLS key in code | `gp.Env(params={"WLSACCESSID": "...", "WLSSECRET": "...", "LICENSEID": 123456})` |
| start quietly | `"OutputFlag": 0` in the same `params`, or an empty environment (lesson 5.3.1) |
| check size before solving | `m.update(); m.NumVars, m.NumConstrs` against 2,000 |
| course runner | `GUROBI_LICENSE_FILE` in `course.env`; mounted read-only at `/licenses/gurobi.lic` |

| Error | Meaning |
| --- | --- |
| 10009 | no license found, or the file named by `GRB_LICENSE_FILE` cannot be opened |
| 10010 | model too large for the size-limited license |

| Term | Meaning |
| --- | --- |
| size-limited license | the license inside the pip package: 2,000 variables and 2,000 linear rows |
| named-user license | tied to one user on one machine |
| WLS | Web License Service: an API key exchanged online for short-lived tokens; works in containers |
| `GRB_LICENSE_FILE` | the environment variable that names the license file's path |

**Further reading.** Gurobi,
[Python API: Env](https://docs.gurobi.com/projects/optimizer/en/current/reference/python/env.html)
(empty environments and `params`),
[Parameters](https://docs.gurobi.com/projects/optimizer/en/current/reference/parameters.html)
(`WLSAccessID`, `WLSSecret`, `WLSToken`, `WLSTokenDuration`); Gurobi support articles
[How do I resolve a "Model too large for size-limited Gurobi license" error?](https://support.gurobi.com/hc/en-us/articles/360051597492-How-do-I-resolve-a-Model-too-large-for-size-limited-Gurobi-license-error)
(the limits and the banner),
[How do I obtain a free academic license?](https://support.gurobi.com/hc/en-us/articles/360040541251)
(named-user, WLS and site licenses, and which work in containers),
[Where do I place the Gurobi license file (gurobi.lic)?](https://support.gurobi.com/hc/en-us/articles/360013417211)
(the default places and `GRB_LICENSE_FILE`) and
[the WLS parameters in code](https://support.gurobi.com/hc/en-us/articles/13232844297489);
Docker Hub, [gurobi/optimizer](https://hub.docker.com/r/gurobi/optimizer) (mounting a license into
Gurobi's own image, and which licenses work in containers).

## Challenges

1. Write a function that builds a model's variables and rows, calls `update()`, and refuses with a
   clear message, before solving, when the size-limited license would.
2. Extend `mask` for a message of your own design that contains a WLS access id (a UUID), and test it.
3. A colleague proposes to copy `gurobi.lic` into the Dockerfile "just for the test image". List
   what goes wrong, using this lesson's sources.

## Design Note: License Is Configuration, Not Code

Every program in this module gets its environment from one place (`quiet_env`, or `open_env` in a
service), and nothing else in the code knows which license is in use. Swapping the size-limited file
for an academic WLS key, or a laptop's file for a container's secret, changes the deployment, never
the model. The same place is where the banner is silenced and the messages are masked, so the rule
"no license data in any output" is kept by construction, not by remembering it in every program.

## The Full Programs

Each program printed the output the lesson shows. Open one to read it whole, change it, and run it
again: Run starts the program on your copy of the code, so the course's own files never change.

**license_errors.py.** What gurobipy says with no license and with a license path that does not
exist, masked (*gurobipy Needs a License Before It Builds Anything*). It needs no license itself.
*Try:* Add a case with `GRB_LICENSE_FILE` set to an empty string and predict the message.

- Program: [license_errors.py](src/license_errors.py)

**size_limit.py.** The size-limited license at its edge, and three GridCap models against it (*The
Size-Limited License Stops at 2,000*). It needs a license. *Try:* Add 2,000 rows to the 2,000-variable
model and predict the result.

- Program: [size_limit.py](src/size_limit.py)

**licensed_env.py.** The environment parameters from a deployment's variables, printed redacted
(*A Container Gets Its License at Run Time*). Its demo needs no license and contacts nothing.
*Try:* Set `LICENSEID` to a word instead of a number and predict what fails.

- Program: [licensed_env.py](src/licensed_env.py)
