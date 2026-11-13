# 5.4.3 License Cost and Fit for Containers

GridCap's planning service will run as a container job on AWS Batch on Fargate (lesson 12.5.2), inside a
private network with no route to the internet: every night a job starts, reads a portfolio snapshot,
solves, writes the plan and stops. Two people now have questions about the solver. Finance asks what
it costs, this year and when the portfolio grows. Operations asks what the container needs for the
solver to run at all: how big the image gets, and whether the solver must reach a license server
before it will solve. GridCap is a fictional utility.

This lesson answers both for the seven solvers of lesson 5.4.1, from two kinds of evidence: what
the runner image itself says about the packages it holds, and what each vendor publishes. Vendor terms
and prices change, so every one of them is quoted with the date of the page it came from, and a
recommendation that uses them carries the date too. Lesson 5.3.4 sets up Gurobi's licenses in detail;
this lesson compares the routes across vendors and asks which fit a container.

## Open-Source Solvers Cost Nothing to License, and Their Licenses Still Have Terms

`footprint.py` reads each solver package's own metadata in the runner image, the record pip saw when
it installed the package, and adds up the size of its installed files:

```python
    dist = md.distribution(package)
    size = sum(f.size or 0 for f in dist.files or [])
    print(f"{package:<10} {dist.version:<10} {declared_license(dist.metadata):<24} {size / 1e6:>11.1f} MB  {inside}")
```

```text
package    version    declared license         installed size  solvers inside
ortools    9.15.6755  Apache 2.0                      82.0 MB  GLOP, PDLP, CP-SAT, and builds of HiGHS, SCIP, CBC, CLP
highspy    1.14.0     MIT License                      6.5 MB  HiGHS
PuLP       3.3.2      MIT                             36.7 MB  a CBC executable per platform
gurobipy   13.0.3     Proprietary                     56.0 MB  Gurobi (needs a license to solve beyond its limits)
pyscipopt: not in the runner image
xpress: not in the runner image
cplex: not in the runner image
```

What it means for the service:

- **One wheel brings four MILP solvers.** OR-Tools (82.0 MB) carries HiGHS, SCIP, CBC and CP-SAT
  (lesson 4.1.2 lists the bundled versions), under its Apache 2.0 license. The service that already
  installs OR-Tools for MathOpt pays nothing more, in money or image size, to have a second solver.
- **The licenses are permissive.** Apache 2.0 (OR-Tools, and SCIP from 8.0.3), MIT (HiGHS, PuLP) and
  EPL 2.0 (CBC, from its README) all allow use inside a closed commercial service. Their terms are
  about notices and redistribution, not fees. One trap: SCIP releases up to 8.0.2 were under the ZIB
  Academic License, so an old pin of SCIP in a commercial service is a licensing question, not only a
  version question.
- **Packages carry more than you use.** PuLP's 36.7 MB holds a CBC executable for each platform it
  supports (Windows, Linux, macOS, ARM), though a Linux container runs one. If image size matters,
  measure it this way rather than guess.
- **No network, no license server.** The runner is started with `docker run --network none`
  (`scripts/runner.py`), and every open-source solver of this module solved there. That is the
  container fit a private-network batch job needs.

The money is not zero, though. A solver you do not pay for is one you support yourself: this course
met several upstream bugs in OR-Tools' solver adapters, each found by a program and worked around
in a lesson: errors whose reason is lost (lessons 2.4.1 and 4.2.4), HiGHS ignoring callbacks
(lesson 4.3.5), and a crash on a cutoff limit (lesson 4.2.4). Budget engineering time for that, not license fees.

## Free Commercial Tiers Stop at a Size GridCap Outgrows

Each commercial vendor has a free tier, and each is capped by model size. The caps, as published on
the pages opened on 2026-11-11:

- **Gurobi**, the license that comes with `pip install gurobipy`: up to 2,000 variables and 2,000
  linear constraints, and 200 variables when the model has quadratic terms (Gurobi support article).
  The gurobipy PyPI page also calls the bundled license an evaluation license for non-production use.
- **CPLEX** Community Edition: up to 1,000 variables and 1,000 constraints (IBM's pricing page).
- **Xpress** Community License: rows plus columns at most 5,000 for linear and mixed-integer
  models, 200 for quadratic and general nonlinear ones, renewed yearly (FICO's license options
  page).

`model_sizes.py` counts GridCap's two model families at every size, the selection model of lesson
5.4.1 built in MathOpt, and the start-year (timing) model of lesson 6.4.2 counted from its
formulation, and checks each against the three caps:

```python
def selection_size(size: str) -> tuple[int, int]:
    pf = generate(size)
    model, _ = build_mathopt(Instance(size, pf.projects, pf.years, dict(pf.budget)))
    return len(list(model.variables())), len(list(model.linear_constraints()))
```

```text
free size limits as published (pages opened 2026-11-11):
  Gurobi pip license        2,000 variables, 2,000 constraints
  CPLEX Community Edition   1,000 variables, 1,000 constraints
  Xpress Community License  5,000 variables + constraints

model              variables    rows   Gurobi    CPLEX     Xpress 
tiny selection             8       6   fits      fits      fits   
tiny timing               13      13   fits      fits      fits   
small selection           40      13   fits      fits      fits   
small timing              80      49   fits      fits      fits   
medium selection         400      85   fits      fits      fits   
medium timing            887     469   fits      fits      fits   
large selection       10,000   1,875   too big   too big   too big
large timing          21,843  11,467   too big   too big   too big
```

Everything up to GridCap medium fits every free tier; GridCap large, the 10,000-project portfolio,
fits none, in either model. The timing model of the medium portfolio, 887 variables and 469 rows,
already uses most of CPLEX's 1,000 variables. So a free tier is enough to put a commercial solver
into the benchmark of lesson 5.4.2 on small and medium instances (and the evaluation licenses of the
next section lift the cap for a trial), but not to run the service on the portfolio GridCap is
growing into. The real price question is the paid license.

<!-- practice 1 -->

## Commercial Prices Are Quotes, So a Recommendation Dates Every Figure

What the vendors' own pages said, as of the pages opened on 2026-11-11:

| Vendor | Published price | License models named on the page |
| --- | --- | --- |
| IBM CPLEX | Developer Subscription from $320.00 USD per authorized user per month, for development only and "not for large-scale firm deployment"; deployment on servers, clusters or clouds priced by IBM on request | machine capacity, user-based, thread-based, desktop |
| Gurobi | no prices: commercial licenses are annual subscriptions, priced by quote | named user, single machine, Web License Service (WLS), floating (token server), compute server, single-use, Gurobi Instant Cloud |
| FICO Xpress | no prices: commercial licenses are by contract | community, academic, evaluation, commercial |

Three consequences for a recommendation:

1. **The only list price is for development, not for the service.** CPLEX's $320.00 per user per
   month (the page also advertised a temporary discount) covers a developer, not a nightly
   production job; every vendor prices deployment by quote. So a cost comparison that a team can
   act on needs quotes, requested for the same deployment shape (one container job, how many
   threads, how many solves a night).
2. **Evaluation licenses make the benchmark free.** Gurobi offers a free full-featured trial (30 days
   for commercial users) and free academic licenses; FICO an evaluation license with no size limit;
   so the harness of lesson 5.4.2 can run a commercial solver on GridCap large before anyone buys
   anything.
3. **Every figure carries its date.** Write "as of the page opened on 2026-11-11" next to each price
   and term, in the recommendation itself. A reader a year later then knows to check, rather than
   trusting a number that has moved.

## In a Container, a Commercial License Needs a Route Out

A popular claim, which lesson 5.3.4 also corrects: "run the solver on AWS Batch on Fargate and the
license problem goes away, because the containers are stateless". It does not. A container is a fresh
machine every time it starts, which is exactly what a license tied to one machine cannot accept.
Gurobi's container pages (its Docker image documentation and its `docker-python` README, opened
2026-11-11) list the routes that do work in a container:

| Route | What the container needs | Fits a private network with no internet? |
| --- | --- | --- |
| Web License Service (WLS) | three credentials (`WLSACCESSID`, `WLSSECRET`, `LICENSEID`) and outbound internet access: the container fetches and renews a license token at start | no |
| token server (floating license) | a license file with connection settings, mounted read-only at run time, and a network path to the token server, which runs outside the container cluster | only if the server is inside the network |
| Compute Server, Cluster Manager, Instant Cloud | a Gurobi service the container reaches over the network | only if that service is reachable |
| the size-limited license in the image | nothing | yes, up to 2,000 variables and constraints |

The same pages say that **NODE and Academic licenses do not work in containers**, and that a license
file should never be baked into the image: mount it at run time, or keep it as a Kubernetes secret. FICO's
Xpress container image ships a time-limited community license for small problems, and its page
says web floating licenses can be attached to a running container: the same pattern, a license
service the container must reach. Outside its image, the `xpress` Python package uses the community
license unless the environment variable `XPRESS` names the folder (not the file) that holds a license
file, `xpauth.xpr`, as its PyPI page explains.

So for GridCap's job, in a private network with no internet, a commercial solver means one of two
changes to the architecture: open an outbound route to the vendor's license service, or run a token
server inside the network and pay for its upkeep. Either is a cost the license price does not show,
and it belongs in the recommendation.

Whatever the route, the service should know at start-up which one it is configured for, and say so
in its log without ever writing a credential there. `license_route.py` makes that decision from
configuration alone, on placeholder values (no credential exists in this course):

```python
def route(settings: dict[str, str], mounted: set[str]) -> str:
    """The license route `settings` (environment and parameters) and `mounted` files configure."""
    present = [k for k in WLS_KEYS if settings.get(k)]
    if present and len(present) < len(WLS_KEYS):
        missing = ", ".join(k for k in WLS_KEYS if k not in present)
        return f"broken WLS setup: missing {missing}"
    if present:
        return "WLS (needs outbound internet)"
    path = settings.get("GRB_LICENSE_FILE")
    if path:
        return f"mounted license file at {path}" if path in mounted else f"GRB_LICENSE_FILE set, but nothing mounted at {path}"
    return "size-limited pip license only"
```

```text
WLS in a Fargate task        license route: WLS (needs outbound internet); set: LICENSEID, WLSACCESSID, WLSSECRET
WLS with the secret missing  license route: broken WLS setup: missing WLSSECRET; set: LICENSEID, WLSACCESSID
file mounted read-only       license route: mounted license file at /licenses/gurobi.lic; set: GRB_LICENSE_FILE
file named, mount forgotten  license route: GRB_LICENSE_FILE set, but nothing mounted at /licenses/gurobi.lic; set: GRB_LICENSE_FILE
nothing configured           license route: size-limited pip license only; set: nothing
```

The two middle lines are the failures that otherwise surface hours later, as a size-limit error on
the first large solve: a WLS setup with one credential missing, and a license path whose mount was
forgotten. The log names which settings are present, never their values. The course runner follows
the same rule for its own optional license: `scripts/runner.py` mounts a file read-only and sets
`GRB_LICENSE_FILE` only when one exists, and none is used in this module.

<!-- practice 2 -->

## Summary

- **Open-source solvers cost nothing to license, and their licenses still have terms.** OR-Tools
  (Apache 2.0, 82.0 MB) brings HiGHS, SCIP, CBC and CP-SAT; SCIP before 8.0.3 was academic-only. The
  real cost is supporting them yourself.
- **Free commercial tiers stop at a size GridCap outgrows.** Gurobi pip 2,000 × 2,000, CPLEX
  Community 1,000 × 1,000, Xpress Community 5,000 rows plus columns (pages opened 2026-11-11): medium
  fits all three, large fits none.
- **Commercial prices are quotes, so a recommendation dates every figure.** The one list price,
  CPLEX's $320.00 per user per month, is for development only.
- **In a container, a commercial license needs a route out**: WLS needs the internet, a token server
  needs a server; NODE and Academic licenses do not work in containers, and no license file goes into
  an image.

## Reference

| Solver | License (as declared or published) | Free tier limit (pages opened 2026-11-11) | Container route without internet |
| --- | --- | --- | --- |
| HiGHS | MIT | none | runs offline |
| SCIP | Apache 2.0 from 8.0.3; ZIB Academic up to 8.0.2 | none | runs offline |
| CBC | EPL 2.0 | none | runs offline |
| CP-SAT | Apache 2.0 (OR-Tools) | none | runs offline |
| Gurobi | commercial | 2,000 variables and 2,000 linear constraints; 200 variables with quadratic terms | token server inside the network |
| CPLEX | commercial | 1,000 variables and 1,000 constraints | not covered by the pages opened |
| Xpress | commercial | 5,000 rows plus columns (linear, MIP); 200 (quadratic, nonlinear) | not covered by the pages opened |

**Further reading:** [OR-Tools on GitHub](https://github.com/google/or-tools) (the Apache 2.0
license and what the suite contains); [HiGHS documentation](https://ergo-code.github.io/HiGHS/dev/)
(MIT license, no third-party dependencies); [SCIP Optimization Suite](https://www.scipopt.org/)
(Apache 2.0 from 8.0.3, ZIB Academic License up to 8.0.2, the ways SCIP is distributed);
[Cbc on GitHub](https://github.com/coin-or/Cbc) (EPL 2.0); [Gurobi pricing and licensing](https://www.gurobi.com/pricing/)
(quote-based annual subscriptions, the seven license models); [Gurobi licensing](https://www.gurobi.com/solutions/licensing/)
(free trial, academic and evaluation licenses); [Gurobi support article on the size-limited license](https://support.gurobi.com/hc/en-us/articles/360051597492)
(Gurobi support: 2,000 variables and 2,000 linear constraints, 200 with quadratic terms);
[gurobipy on PyPI](https://pypi.org/project/gurobipy/) (the bundled license for non-production use);
[How do I set up a Web License Service (WLS) license?](https://support.gurobi.com/hc/en-us/articles/13232844297489-How-do-I-set-up-a-Web-License-Service-WLS-license)
(the three credentials, internet access); [gurobi/optimizer on Docker Hub](https://hub.docker.com/r/gurobi/optimizer)
and [Gurobi docker-python](https://github.com/Gurobi/docker-python) (WLS, mounted license files, token
servers; NODE and Academic licenses do not work in containers; never bake a license into an image);
[IBM ILOG CPLEX Optimization Studio pricing](https://www.ibm.com/products/ilog-cplex-optimization-studio/pricing)
(Community Edition limits, the Developer Subscription price, deployment by request);
[FICO Xpress license options](https://www.fico.com/en/fico-xpress-trial-and-licensing-options)
(the four license types and the community limits); [xpress on PyPI](https://pypi.org/project/xpress/)
(the community license recognized automatically; a full license found through the `XPRESS` folder);
[ficoxpress/xpress-solver on Docker Hub](https://hub.docker.com/r/ficoxpress/xpress-solver) (a
time-limited community license in the image, web floating licenses).

## Challenges

1. Add GridCap large's timing model at half the projects to `model_sizes.py` (generate `large`, keep
   every other project). Predict which free tier it fits, if any.
2. Measure the installed size of `highspy` against the HiGHS inside `ortools`. Would a service that
   only needs HiGHS be smaller with `highspy` alone? What would it lose?
3. Extend `route` to refuse a license file path that lies inside the image's application folder, so a
   baked-in license fails the start-up check.

## Design Note: Put the License Route in the Architecture Diagram

A commercial solver in a container is not a library choice; it is a network dependency (a license
service or a token server), a secret to manage, and a failure mode at start-up. Draw it in the
architecture next to the database and the object store, with who owns it and what happens when it is
unreachable. If the answer is "the nightly job fails", the recommendation has to price that risk as
well as the license.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**footprint.py.** Each solver package's declared license and installed size, read from the runner
image's own metadata (*Open-Source Solvers Cost Nothing to License*). *Try:* Add `"Pyomo"` to the
list. Predict its declared license.

- Program: [footprint.py](src/footprint.py)

**model_sizes.py.** GridCap's selection and timing models at every size, against the three free
tiers (*Free Commercial Tiers Stop at a Size GridCap Outgrows*). *Try:* Add a 200-variable quadratic
cap for Gurobi and a model with a quadratic objective. Predict which sizes still fit.

- Program: [model_sizes.py](src/model_sizes.py)

**license_route.py.** The start-up check that names the configured license route and never a
credential (*In a Container, a Commercial License Needs a Route Out*). *Try:* Configure both WLS
credentials and a mounted file. Predict which route wins, and decide whether it should.

- Program: [license_route.py](src/license_route.py)
