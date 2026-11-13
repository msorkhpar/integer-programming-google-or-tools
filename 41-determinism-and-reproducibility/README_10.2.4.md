# 10.2.4 Versioned Input Snapshots, Pinned Solvers and Run Manifests

Two years after the 2026 plan of record, GridCap's regulator asks for it to be reproduced: same
inputs, same model, same result, or an explanation of every difference. The planning team still has
the plan. Does it have what produced it? Which portfolio file, after which edits? Which budget
figures? Which version of OR-Tools, which solver, which seed and limits? If any of these was not
written down at the time, the plan cannot be reproduced, only re-derived, and a re-derived plan may
differ for all the reasons of lessons 10.2.1 to 10.2.3.

This lesson writes down everything a run read, in a form that a later run can be compared with
byte for byte: a **snapshot** of the inputs with a digest that names it, **pinned** solver versions
checked at start-up, and a **run manifest** that records inputs, software and result in one
canonical document. Lesson 7.1.3 introduced snapshots for scenarios; lesson 12.2.3 stores them
in a service. GridCap is a fictional utility's portfolio.

The model is lesson 10.2.1's timing model, unchanged; this lesson changes only what is recorded
about a solve.

## A Snapshot Is the Digest of the Inputs in One Canonical Form

A **snapshot** is the set of a model's inputs, frozen: the portfolio, the budgets, the overrides,
the settings. To compare two snapshots, or to name one in a report, write it out in one
**canonical form**, a text that equal inputs always produce and different inputs never do, and take
its SHA-256 **digest**: a 64-hex-digit fingerprint that changes completely if a single character of
the text changes. The hard part is the canonical form. `snapshot.py` tries the usual ways to get it
wrong:

```python
a = {"budget": {"2027": 8890, "2028": 8120}, "force_in": ["P024"]}
b = {"force_in": ["P024"], "budget": {"2028": 8120, "2027": 8890}}          # same inputs, built in another order
print("insertion order, json.dumps          ", digest(json.dumps(a)), digest(json.dumps(b)))
print("insertion order, sort_keys=True      ", digest(json.dumps(a, sort_keys=True)), digest(json.dumps(b, sort_keys=True)))
print("insertion order, str()               ", digest(str(a)), digest(str(b)))
```

```text
insertion order, json.dumps           82fa854f3e41 3546d7e1adfb
insertion order, sort_keys=True       82fa854f3e41 82fa854f3e41
insertion order, str()                064d599e60f2 b68f23bc610a
a set in the inputs                   Object of type set is not JSON serializable
str(set) digested, hash seed 1        eb4de6ee9e9b
str(set) digested, hash seed 2        feb1d3d8c170
sorted(set) digested                  e8a8a638ccc7
0.1 + 0.2 and 0.3 as JSON             0.30000000000000004 0.3
int key 2027 and str key '2027'       True
GridCap small content hash            29d5349c5b5a
same, rebuilt from the generator      29d5349c5b5a
2029 budget $1k lower                 f686fc39a831
```

Line by line:

- **Dict order.** `json.dumps` writes a dict's keys in the order they were inserted, so the same
  inputs built in another order give another digest. `sort_keys=True` writes them sorted, and the
  digests agree. `str()` of a dict follows insertion order too (the third line), so code that builds
  the dict the same way writes the same text on every run.
- **Sets.** JSON has no set, so `json.dumps` refuses one. The tempting fix, `str(the_set)`, writes the
  set in its iteration order, which depends on the process's hash salt (lesson 10.2.1): two processes,
  two digests for the same set. Sort it first, and it digests the same everywhere.
- **Floats.** `0.1 + 0.2` is written `0.30000000000000004`, not `0.3`: two computations of "the same"
  amount can differ in their last digit (lesson 10.1.1) and so in their digest. Keep money in whole
  units ($k as integers, as GridCap does) or round it before it enters a snapshot.
- **Key types.** JSON keys are always strings, so `{2027: 1}` and `{"2027": 1}` write the same text.
  Usually that is what you want; just know that the digest cannot tell them apart.
- **GridCap's own hash** (`Portfolio.content_hash()`, which uses `sort_keys` and fixed separators)
  is the same when the portfolio is generated again and changes when one budget moves by $1k.

The course's canonical form, used for every manifest in this module, is three settings of
`json.dumps`:

```python
def canonical(obj) -> bytes:
    """One byte string per value: sorted keys, no spaces, ASCII only."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
```

`sort_keys` fixes the order, `separators` fixes the spacing, and `ensure_ascii` writes any non-ASCII
character as an escape, so the bytes do not depend on a text encoding. Lists keep their order, so a
list in a snapshot must be one whose order means something, or be sorted before it goes in.

<!-- practice 1 -->

## The Solver's Version Is an Input Too: Pin It and Record It

Lesson 10.2.1 listed the solver and its version among a run's inputs, and Gurobi's determinism
article makes "the same version" a condition of getting the same result. The version you have is
whatever the environment installed, so a reproducible run **pins** it (names the exact version in
the environment's requirements; this course's runner image pins every package) and **checks** it,
because a pin in a file does not stop someone running the code in another environment:

```python
def check_pins(pins: dict[str, str]) -> list[str]:
    """Every package whose installed version is not the pinned one, as 'name: pinned X, found Y'."""
    return [f"{name}: pinned {want}, found {version(name)}"
            for name, want in sorted(pins.items()) if version(name) != want]
```

```text
ortools 9.15.6755 carries: libhighs.so.1, libortools.so.9, libscip.so.10.0
highspy 1.14.0 (HiGHS packaged on its own, apart from the copy in the OR-Tools wheel)
pins as installed: all match
a stale pin:       ['ortools: pinned 9.14.6206, found 9.15.6755']
```

The first line answers a question that trips people up: which HiGHS does MathOpt run? The OR-Tools
wheel carries its own HiGHS and SCIP libraries, and OR-Tools' release notes for v9.15 name them:
HiGHS 1.12.0 and SCIP 10.0.0. The `highspy` package installed beside it is HiGHS 1.14.0, a different
version used only by code that imports `highspy` (Pyomo's and PuLP's HiGHS interfaces, for example).
So the OR-Tools version pins both the HiGHS and the SCIP that MathOpt runs, and the `highspy` version
pins something else. A manifest records the OR-Tools version for the first, and `highspy`'s only for
runs that use it.

`check_pins` returns the mismatches rather than raising, so the caller decides; a service should
refuse to start on any, and a harness (lesson 10.2.5) should record them. The last line shows what
a stale pin looks like.

## A Run Manifest Records What Went In and What Came Out, and Leaves Out the Clock

A **run manifest** is the record of one solve that another run is compared with. It holds:

- **inputs**: the snapshot's digest and the model's options;
- **solver**: its name and every parameter passed;
- **versions**: Python, OR-Tools (and gurobipy when it ran), and the platform's operating system
  and processor architecture;
- **result**: status, objective, bound, the plan and its digest, and the work done (nodes,
  iterations, branches, deterministic time).

`solve_once.py` writes it at the end of every run:

```python
    manifest = {"inputs": {"snapshot": portfolio.content_hash(), "size": config["size"],
                           "objective": config["objective"], "order": config.get("order", "given")},
                "solver": {"name": config["solver"], "params": config.get("params", {})},
                "versions": versions(config["solver"]),
                "result": result}
    return {"manifest": manifest, "clock": {"wall_seconds": round(time.perf_counter() - started, 3)}}
```

```python
def versions(solver: str) -> dict:
    """The software a run depended on. OR-Tools' wheel carries its own HiGHS and SCIP libraries."""
    found = {"python": platform.python_version(), "ortools": version("ortools"),
             "platform": f"{platform.system()}-{platform.machine()}"}
    if solver == "gurobi":
        found["gurobipy"] = version("gurobipy")
    return found
```

Two runs of GridCap small on HiGHS, one manifest printed field by field (the plan cut to its first
three starts), and the two compared:

```text
inputs.objective     "npv"
inputs.order         "given"
inputs.size          "small"
inputs.snapshot      "29d5349c5b5ab600ecfb86b6d3c1fbe3cd0adaa21f7abfec385b4d3387a195e7"
result.bound         24260.0
result.objective     24260.0
result.plan          [["P001",2028],["P003",2031],["P005",2029],...]  (27 starts)
result.plan_digest   "092777a3fdd1"
result.stats         {"nodes":31,"simplex_iterations":3577}
result.status        "OPTIMAL"
solver.name          "highs"
solver.params        {"relative_gap_tolerance":0.0}
versions.ortools     "9.15.6755"
versions.platform    "Linux-x86_64"
versions.python      "3.14.7"
manifest sha256  4fbb9df414248815 | second run 4fbb9df414248815
same bytes: True
kept out of the manifest: ['wall_seconds']
```

The two runs wrote identical bytes, so their SHA-256 digests match. Three choices made that
possible.

**The clock is kept apart.** The wall time of a run is a fact about the machine and its load, not
about the plan; it differs on every run (lesson 10.2.1), so a manifest that held it could never
match another. `run` returns it beside the manifest, under `clock`, where a log or a dashboard can use
it. The same goes for anything else that varies by run and not by inputs: a start time, a process
id, a temporary directory.

**Nothing names the machine or a person.** The platform field says `Linux-x86_64`, an operating
system and an architecture. It does not say which machine: no host name, no user name, no home
directory, no license id. Those would break byte equality between machines, and a manifest is
shared, archived and attached to filings, so it must not carry anything that identifies a person or
a machine. Lesson 5.3.4 applies the same rule to Gurobi's license messages.

**The work done is in.** Nodes and iterations are not needed to use the plan, but they repeat when a
run truly repeats (lesson 10.2.2), and they differ first when something changed. A clock-limited run
that happened to return the same plan still shows different iteration counts (lesson 10.2.1), so
keeping them makes the manifest stricter than the plan alone.

The plan itself is stored sorted (`sorted([pid, t] ...)`), so the order in which the code collected
the starts never reaches the bytes.

<!-- practice 2 -->

## Summary

- **A snapshot is the digest of the inputs in one canonical form.** Sort keys, sort sets, fix the
  separators, keep money in whole units; then equal inputs give equal digests in every process.
- **The solver's version is an input too: pin it and record it.** The OR-Tools wheel carries its
  own HiGHS (1.12.0 in v9.15) and SCIP; `highspy` is another HiGHS. Check pins at start-up.
- **A run manifest records what went in and what came out, and leaves out the clock.** Inputs,
  solver and parameters, versions, and the result with its work counts, in canonical bytes; wall
  time and anything naming the machine or a person stay out.

## Reference

| Field of a manifest | Why it is there |
| --- | --- |
| `inputs.snapshot` | the digest of the data; equal digests mean equal data |
| `inputs.*` (model options) | the question asked and how the model was built |
| `solver.name`, `solver.params` | seed, threads, limits, tolerances: each changes the path (10.2.2) |
| `versions.*` | Python, OR-Tools (which fixes MathOpt's HiGHS and SCIP), gurobipy, OS and architecture |
| `result.status`, `objective`, `bound` | what was proved |
| `result.plan`, `plan_digest` | the plan itself, sorted, and its fingerprint |
| `result.stats` | work counts: they differ first when a run changed |
| *not in it:* wall time, start time | vary on every run |
| *not in it:* host, user, paths, license ids | name a machine or a person |

| Canonical JSON | Setting |
| --- | --- |
| key order | `sort_keys=True` |
| spacing | `separators=(",", ":")` |
| encoding | `ensure_ascii=True`, then `.encode("ascii")` |
| sets | sorted lists before they go in |
| floats | whole units, or rounded before they go in |

**Further reading:** [OR-Tools releases](https://github.com/google/or-tools/releases) (v9.15 bundles
HiGHS 1.12.0 and SCIP 10.0.0);
[Is Gurobi deterministic? (Gurobi support)](https://support.gurobi.com/hc/en-us/articles/360031636051)
(the same version and machine as conditions for the same result);
[`json`](https://docs.python.org/3/library/json.html) (`sort_keys`, `separators`, `default`,
`ensure_ascii`, and int keys written as strings);
[`hashlib`](https://docs.python.org/3/library/hashlib.html) (SHA-256 and `hexdigest`);
[Python data model, `object.__hash__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__)
(why `str` of a set is not canonical).

## Challenges

1. Add the HiGHS seed to the config of `manifest.py` and run it twice with seeds 1 and 2. Predict
   which manifest fields differ.
2. A colleague adds `"run_id": str(uuid.uuid4())` to the manifest "for traceability". What happens to
   the comparison, and where should the id go instead?
3. Two machines run the same manifest config: one `Linux-x86_64`, one `Darwin-arm64`. Their
   manifests differ in `versions.platform` only. Is that a failure? What would you check next?

## Design Note: One Canonical Function, Used Everywhere

Every digest in this module goes through one function, `canonical`. A snapshot hashed one way and a
manifest compared another way will disagree for reasons that have nothing to do with the solve. Put
the canonical form in one place, test it once (practice 1 does), and call it from the snapshot, the
manifest and the harness alike.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**snapshot.py.** What changes a digest and what must not: dict order, sets, `str` of a set across hash
seeds, floats, key types, and GridCap's content hash (*A Snapshot Is the Digest of the Inputs*).
*Try:* Add `ensure_ascii=False` and a project named `"Pöhl"`. Predict whether the digest changes.

- Program: [snapshot.py](src/snapshot.py)

**pinned.py.** The libraries in the OR-Tools wheel, the separate `highspy`, and a pin check
(*The Solver's Version Is an Input Too*). *Try:* Pin `numpy` to a version you do not have. Predict the
output line.

- Program: [pinned.py](src/pinned.py)

**manifest.py.** Two runs of one config, the manifest printed field by field and compared byte for
byte (*A Run Manifest Records What Went In and What Came Out*). *Try:* Switch the solver to `"scip"`.
Predict which fields change.

- Program: [manifest.py](src/manifest.py)
