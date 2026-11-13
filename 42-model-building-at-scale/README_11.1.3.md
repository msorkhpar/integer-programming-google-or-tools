# 11.1.3 A Generator for 10,000-Project Portfolios

Performance work needs data at the size you will run, and GridCap's planners will not hand over
next year's 10,000 real projects to a test suite. So the course generates them: `generate("large")`
in the course's `gridcap` package makes a fictional portfolio of 10,000 projects over 10 years. A generated portfolio is
only useful if it is the same portfolio every time someone asks for it, and if every portfolio it
can make is one the model can use. This lesson takes GridCap's generator apart for those two
properties: reproducible from a seed, and checked by a test of its invariants at many seeds, not
one.

## The Model

The generated portfolio feeds the timing model of lessons 6.4.1 and 6.4.2, which this lesson builds
once per seed to check that it is feasible.

**Sets.** $`P`$ the projects; $`Y`$ the plan's years; $`T_i \subseteq Y`$ the start years project
$`i`$ may use; $`M \subseteq P`$ the must-do projects; $`\mathcal{G}`$ the alternative groups;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$ and lag $`L_c`$ years.

**Parameters.** $`\text{npv}_{i,t}`$ ($k); $`c_{i,k}`$, what project $`i`$ spends in its $`k`$-th
year of work ($k); $`B_y`$, the budget of year $`y`$ ($k).

**Variables.** $`x_{i,t} \in \{0, 1\}`$ for every $`i \in P`$ and $`t \in T_i`$.

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
\sum_{i \in P} \sum_{t \in T_i,\, t \le y} c_{i,\,y-t}\, x_{i,t} &\le B_y && \forall y \in Y && \text{(budget}_y)
\end{aligned}
```

## The Same Seed Gives the Same Portfolio, in This Process and in a Fresh One

A **seed** is the number a pseudo-random generator starts from: the same seed gives the same
sequence of "random" numbers, so the same seed gives the same portfolio. GridCap's generator is
built so that this holds byte for byte, on any machine, by three choices its docstring states:

- **One stream, one method.** It draws every random number from one `random.Random`, seeded from
  the seed and the size, and calls only its `random()` method. Python's documentation guarantees
  that `random()` keeps producing the same sequence for the same seed across Python versions; it
  makes no such promise for the helpers built on top (`randint`, `choice`, `shuffle`), whose
  algorithms may change. The generator builds its own `between` and `pick` on `random()` instead.
- **Its own integer arithmetic.** Money is rounded to integers by the generator's own code, so no
  library's rounding can change a cost.
- **No numpy random numbers.** numpy promises the same stream for its `Generator` methods only on
  the same build of numpy on the same machine; a feature release may change them. That is fine for
  a simulation and wrong for a dataset whose hash is pinned.

`Portfolio.content_hash()` is the SHA-256 of the portfolio's canonical JSON (sorted keys, no
spaces), so two portfolios with equal hashes are equal field for field. `gridcap`'s own tests pin the
hash of every size at the default seed. `reproducible.py` checks the large one, then generates it
again in two fresh Python interpreters, each with a different `PYTHONHASHSEED`, the variable that
salts Python's hashing of strings (so a `set` of project ids iterates in a different order):

```python
def in_fresh_interpreter(hash_seed: str) -> str:
    """Generate large in a new Python process whose string hashing is salted differently."""
    env = {**os.environ, "PYTHONHASHSEED": hash_seed}
    return subprocess.run([sys.executable, "-c", CHILD], env=env, capture_output=True, text=True,
                          check=True).stdout.strip()
```

```text
seed 2027: 10,000 projects, hash 092cac4f6f56f699..., pinned: True
same seed, generated again here:      True
fresh interpreter, PYTHONHASHSEED=1: True
fresh interpreter, PYTHONHASHSEED=2: True
seed 2028: hash 1c17c7e11340be98..., projects with the same id and cost profile: 25
seed 2029: hash 236a5e6e1ae0aa79..., projects with the same id and cost profile: 26
```

The same seed gives the same 10,000 projects in this process and in processes that hash strings
differently: nothing in the generator depends on the order of a `set` or a `dict` built from
hashed keys. Another seed gives another portfolio; the 25 and 26 projects that match by id and cost
profile are coincidences among 10,000 draws. The hash is what a run manifest records to say which
portfolio a plan was made from (lesson 10.2.4).

Generating 10,000 projects is not where a run's time goes. One run of the program on the author's
machine; yours will differ:

<!-- unverified -->
```text
measured: generate('large') median 0.167s (range 0.158-0.273, n=5)
```

## One Shared Stream Ties Every Draw to Every Draw Before It

A single stream has a cost that shows up the first time the generator changes. Every draw takes
the next number from the stream, so adding one draw anywhere shifts every number after it, and every
project generated after that point changes. `streams.py` shows it on a toy generator of (kind,
cost, earliest start) triples, written two ways. Version 2 adds one draw, a crew size, for
distribution projects only. One way draws everything from one shared stream; the other gives each
project a stream of its own, seeded from the portfolio's seed and the project's position:

```python
def stream_per_project(n: int, seed: int, version: int = 1) -> list[tuple]:
    out = []
    for i in range(n):
        draw = random.Random(seed * 1_000_000 + i)   # project i's own stream: below a million projects, no two share one
        kind = KINDS[min(int(draw.random() * 3), 2)]
        cost = 100 + int(draw.random() * 900)
        start = 2027 + int(draw.random() * 5)
        if version == 2 and kind == "distribution":
            draw.random()
        out.append((kind, cost, start))
    return out
```

Each project prints as its kind's first letter, its cost and its earliest start (`d162/2027` is a
distribution project costing 162 that may start in 2027):

```text
one shared stream:
  version 1: t235/2030 t582/2028 t556/2027 d162/2027 d844/2027 t664/2031 d457/2031 t872/2028
  version 2: t235/2030 t582/2028 t556/2027 d162/2027 v211/2028 d952/2029 v141/2031 t229/2027
  projects that changed: [5, 6, 7, 8]
  first 8 of 10,000 equal the 8: True
a stream per project:
  version 1: v829/2031 t123/2028 t222/2031 d906/2031 v608/2027 t785/2031 v877/2030 d662/2029
  version 2: v829/2031 t123/2028 t222/2031 d906/2031 v608/2027 t785/2031 v877/2030 d662/2029
  projects that changed: []
  first 8 of 10,000 equal the 8: True
```

- **With one shared stream, project 4 (the first distribution project) took the new draw, and every
  project after it changed**: different kinds, costs and starts, though nothing about them was
  meant to change. Every test and every lesson output that used them would change too.
- **With a stream per project, nothing that existed changed.** The new draw comes last in each
  project's own stream, so it moves no other number.
- **Both are prefix-stable** here: the first 8 projects of a 10,000-project portfolio are the 8-project
  portfolio, because each project's draws happen in one place, in order. A generator that drew all
  kinds first, then all costs, would lose that: the cost of project 1 would come after 10,000 kinds
  in one portfolio and after 8 in the other.
- **Per-project seeds must not collide.** `seed * 1_000_000 + i` gives every (seed, project) pair its
  own number while there are fewer than a million projects. The tempting `seed + i` would give
  project 1 of seed 7 the stream of project 0 of seed 8, so two "different" portfolios would share
  almost every project, shifted by one.

GridCap uses one shared stream, and accepts the cost knowingly: its tests pin each size's hash, so
any change to the generator fails them, and the change then has to be made on purpose, with every
lesson's output regenerated in the same commit (a comment above the pinned hashes in
GridCap's generator tests says so). A generator that will keep growing fields is better
served by a stream per item.

<!-- practice 1 -->

## Invariants State What Every Portfolio Must Satisfy, and a Test Checks Them at Many Seeds

A reproducible generator can still make a portfolio the model cannot use. An **invariant** is a
rule every portfolio must satisfy whatever the seed: something a builder, a test or a lesson relies
on without checking. GridCap's are the ones its generator was written to guarantee, and the ones the
timing model needs:

| Invariant | Why the model needs it |
| --- | --- |
| project ids are unique | variable and row names are made from them, and names must be distinct |
| every project's asset exists | asset-risk models (section 7) join projects to assets |
| each window lies inside the horizon, with the work ending by the last year | no cost lands in a year with no budget row |
| an NPV for every allowed start | every $`x_{i,t}`$ has an objective coefficient |
| a child's parent exists and can start at least the lag before the child's latest start | otherwise every $`\text{after}_{c,t}`$ forces the child to 0 |
| alternatives come in pairs | the $`\text{alt}_g`$ rows describe repair or replace |
| must-dos fit the yearly budget, started as early as they can | otherwise $`\text{must}_i`$ and $`\text{budget}_y`$ conflict |
| must-dos fit the regional caps the same way | models with regional caps were infeasible before this held |

`invariants.py` writes each one as a check that returns a readable line per violation, so a good
portfolio gives an empty list. Two of them:

```python
        if not first <= q.earliest_start <= q.latest_start or q.latest_start + q.duration - 1 > last:
            out.append(f"window inside the horizon: {q.project_id} {q.earliest_start}-{q.latest_start}, "
                       f"{q.duration} years of work")
```

```python
    out += [f"must-dos fit the yearly budget: {y} needs {s:,} of {p.budget[y]:,}"
            for y, s in year_spend.items() if s > p.budget[y]]
```

The rules are necessary, but the property that matters most is the one they are for: the model
has a feasible plan. That can be checked directly, without a solver. The plan "every must-do at its
earliest start, nothing else" should satisfy every row, so build the model (with lesson 11.1.2's
matrix builder, which takes a tenth of a second) and multiply. With the matrix as three arrays, the
value of every row for a plan $`x`$ is $`Ax`$, and `np.bincount` sums each row's terms in one call:

```python
    m = proto.linear_constraint_matrix
    rows, col, coef = np.array(m.row_ids), np.array(m.column_ids), np.array(m.coefficients)
    activity = np.bincount(rows, weights=coef * x[col], minlength=len(proto.linear_constraints.ids))
    lb, ub = np.array(proto.linear_constraints.lower_bounds), np.array(proto.linear_constraints.upper_bounds)
    return bool(np.all((lb - 1e-9 <= activity) & (activity <= ub + 1e-9)))
```

The program checks GridCap large at ten seeds, then plants a violation, a must-do made to cost one
whole year's budget more, to show that the checks can fail:

```text
GridCap large at 10 seeds, 8 rules: 0 violations; the must-do plan fits the model at 10 of 10 seeds
must-do projects per seed: 861 to 938

planted: P00041 made to cost one whole 2035 budget more
   must-dos fit the yearly budget: 2035 needs 1,069,530 of 918,450
   must-dos fit the regional caps: ('Valley', 2035) needs 949,220 of 418,690
   the must-do plan fits the model: False
```

Why ten seeds, when `gridcap`'s own tests already check these rules? Because they check them at
the default seed only, and on tiny, small and medium: the large portfolio and every other seed were
never checked. An invariant is a claim about *every* seed. A test at one seed checks one
portfolio; a test at many seeds (the module's tests use three for large, and the program ten) is
what makes "the generator never does this" believable. A check that has never failed proves little
either, which is why the program plants a violation and watches both the rule and the feasibility
check catch it. The two answer different questions: the plant shows that a check can fail, not
that other seeds pass it, and only the checks at other seeds show that.

<!-- practice 2 -->

## Count What the Generator Puts Into the Model

The generator's knobs decide the model's size, family by family. `scale.py` counts both sides for
every size, using lesson 11.1.2's entry tables:

```text
size    projects  must  child groups  starts   once  alt  after budget  nonzeros  budget nz
tiny           8     1      1      1      13      8    1      1      3        34         16
small         40     4      2      2      80     40    2      2      5       210        115
medium       400    39     18     18     887    400   18     41     10     2,550      1,426
large     10,000   871    419    575  21,843 10,000  575    882     10    63,048     35,404
```

Here `once` counts the once and must rows together (one per project), `starts` the variables, and
`budget nz` the nonzeros in the budget rows alone. What the table says about scale:

- **Variables grow with projects times window length**: 2.0 starts per project on small, about 2.2
  on medium and large, so 10,000 projects make 21,843 binaries.
- **Most rows are one per project.** The once/must rows are 10,000 of large's 11,467; the after rows
  grow with children times their windows (882 rows for 419 children).
- **The budget rows are few and dense.** Ten rows hold 35,404 of the 63,048 nonzeros, more than
  half, because every start variable pays into every year its project works. Each one ties
  thousands of projects together, where a once row ties a project's two or three starts.

A generator for performance work should be checked for this too: a portfolio ten times larger whose
structure is different (no children, no must-dos, all one-year projects) would measure a different
model, and the speed-ups of lesson 11.1.2 would not carry over.

## Summary

- **The same seed gives the same portfolio, in this process and in a fresh one.** GridCap draws only
  `random()` from one seeded stream, does its own integer arithmetic, and pins each size's content
  hash.
- **One shared stream ties every draw to every draw before it.** A new draw changes every later
  item; a stream per item, seeded so no two collide, changes none.
- **Invariants state what every portfolio must satisfy, and a test checks them at many seeds.**
  Eight rules, plus a feasible plan checked as $`Ax`$ within the row bounds, hold at ten seeds of
  GridCap large; a planted overspend breaks both.
- **Count what the generator puts into the model.** GridCap large is 21,843 binaries and 11,467
  rows, and its 10 budget rows hold more than half of the 63,048 nonzeros.

## Reference

| Property | How to get it | How to test it |
| --- | --- | --- |
| reproducible | one seeded `random.Random`, only `random()`, own rounding | equal `content_hash()` here and in a fresh interpreter |
| different seeds differ | the seed enters every stream | unequal hashes for two seeds |
| stable when the generator grows | a stream per item, seeded `seed * K + i` with `K` above the item count | add a draw; earlier items unchanged |
| prefix-stable | each item's draws in one place, in order | first $`k`$ of $`n`$ items equal the $`k`$-item portfolio |
| usable by the model | invariants checked in code | no violations at many seeds, a planted violation caught |
| feasible | a witness plan | $`\text{lb} \le Ax \le \text{ub}`$ for every row |

**Further reading:** [MathOpt `model.proto` (OR-Tools source, v9.15)](https://github.com/google/or-tools/blob/v9.15/ortools/math_opt/model.proto) (the matrix as row ids, column ids and coefficients, which `witness_fits` multiplies); [Python `random`, Notes on reproducibility](https://docs.python.org/3/library/random.html#notes-on-reproducibility) (only `random()` is guaranteed to repeat across versions for a given seed); [numpy random, Compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html) (`Generator` streams repeat only on the same build, machine and environment).

## Challenges

1. Generate GridCap medium at seed 2027 and take the first 400 projects of GridCap large. Are they
   the same projects? Explain from the generator's seeding.
2. Add an invariant: "a must-do project is never a child". Does the witness plan rely on it? Check it
   at the program's ten seeds, then plant a must-do child and confirm the new rule catches it.
3. Rewrite the toy generator of `streams.py` with numpy's `Generator`, one per project. Which of the
   Reference table's properties survive a numpy upgrade?

## Design Note: A Generator Is Code Under Test Like Any Other

It is tempting to treat generated data as a fixture: produced once, trusted forever. But the
generator is code, and its output is the input of every lesson and test downstream. So it gets what
other code gets: a pinned output for the cases everyone uses (the content hashes), properties
checked over many inputs (the invariants at many seeds), and a planted failure to prove the checks
can fail. When a generator change breaks a pinned hash, that is the system working: decide whether
the change is wanted, then regenerate on purpose.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change. The timing you get is your machine's, and it will differ from the one on this page.

**reproducible.py.** GridCap large's hash against the pinned one, generated again here and in two fresh interpreters, and at two other seeds (*The Same Seed Gives the Same Portfolio*). *Try:* Change `CHILD` to generate `medium`. Which line then fails, and why?

- Program: [reproducible.py](src/reproducible.py)

**streams.py.** A toy generator with one shared stream and with a stream per project, before and after adding one draw (*One Shared Stream*). *Try:* Move the new draw to before the cost in `stream_per_project`. Predict which projects change.

- Program: [streams.py](src/streams.py)

**invariants.py.** Eight invariants and a feasibility witness, at ten seeds of GridCap large, and a planted violation (*Invariants State What Every Portfolio Must Satisfy*). *Try:* Plant a child whose parent id does not exist and predict the line `violations` prints.

- Program: [invariants.py](src/invariants.py)

**scale.py.** Projects, relationships, rows and nonzeros, family by family, for every GridCap size (*Count What the Generator Puts Into the Model*). *Try:* Add a column for the average number of nonzeros per budget row, and predict it for large first.

- Program: [scale.py](src/scale.py)

**matrix_builder.py, tables.py.** The tables and the matrix builder of lesson 11.1.2, which `invariants.py` and `scale.py` reuse.

- Library: [matrix_builder.py](src/matrix_builder.py)
- Library: [tables.py](src/tables.py)
