# 1.2.2 Sparse Model Matrices and Why Solvers Rely on Sparsity

GridCap's planning team adds a rule from the regulator: each of the four regions has its own
budget in each year, on top of the company-wide one. On the tiny portfolio the model matrix grows
from 7 rows to 17. On the large portfolio, 10,000 projects over ten years, it has 1,044 rows, and
the NumPy array of lesson 1.2.1 would hold 10,440,000 numbers. Almost all of them are zero. This
lesson counts those zeros, stores only the numbers that are not, and shows that a solver is handed
the model in exactly that form. Four rules, one per heading.

GridCap is a fictional utility; none of its numbers describe a real one. Every project in this
lesson still starts in its earliest start year, as in lesson 1.2.1.

## Most Entries of a Model Matrix Are Zero

The model matrix here has four kinds of rows: a budget per year (`budget_2027`), a budget per
region and year (`region_Valley_2028`), one parent row per child project
($`x_c - x_{p(c)} \le 0`$) and one row per alternative group ($`\sum_{j \in g} x_j \le 1`$).
A **nonzero** is an entry of the matrix that is not 0, and the **density** is the share of entries
that are nonzeros.

```python
for size in ("tiny", "small", "medium", "large"):
    A, b, names = csr(generate(size))
    rows, cols = A.shape
    print(f"{size:6} {rows:>5} {cols:>6} {rows * cols:>10,} {A.nnz:>8,} {A.nnz / (rows * cols):>8.2%}"
          f" {rows * cols * 8 / 1e6:>9.3f} {stored_bytes(A) / 1e6:>7.3f}")
```

```text
size    rows   cols    entries nonzeros  density  dense MB  CSR MB
tiny      17      8        136       26   19.12%     0.001   0.001
small     29     40      1,160      122   10.52%     0.009   0.002
medium    86    400     34,400    1,368    3.98%     0.275   0.023
large   1044  10000 10,440,000   34,610    0.33%    83.520   0.562
```

The density falls as the portfolio grows: 19% on tiny, a third of one percent on large. The
reason is in the rows, not in GridCap's numbers:

```text
large: 10,000 columns
budget  rows:   10, nonzeros per row:  1092 to  1804, mean  1631.1
region  rows:   40, nonzeros per row:   264 to   480, mean   407.8
parent  rows:  419, nonzeros per row:     2 to     2, mean     2.0
alt     rows:  575, nonzeros per row:     2 to     2, mean     2.0
```

A project only spends in the one to three years it is worked on, so it appears in few of the ten
budget rows. It belongs to one region, so it appears in at most three of the forty region rows. A
parent row touches two projects, whatever the size of the portfolio. Most rows of a real model are
like the parent row: a local rule about a few variables. Add projects and you add columns and
rows, while each row keeps about the same number of nonzeros, so the share of nonzeros keeps
falling. A matrix where most entries are zero is called **sparse**; one stored with every entry is
**dense**.

## Store Only the Nonzeros: Triplets, Then Compressed Rows

The simplest sparse form lists each nonzero as a **triplet** (row, column, value). This is also
called *coordinate* or *COO* form, and it is how a model is naturally built: each rule adds its
entries as it goes.

```text
first rows as triplets (row, col, value):
  (0, 2, 980)  budget_2027 x P003
  (0, 4, 250)  budget_2027 x P005
  (0, 6, 290)  budget_2027 x P007
  (0, 7, 580)  budget_2027 x P008
  (1, 0, 2150)  budget_2028 x P001
  (1, 1, 2730)  budget_2028 x P002
  (1, 2, 1490)  budget_2028 x P003
  (1, 3, 2000)  budget_2028 x P004
  (1, 5, 840)  budget_2028 x P006
17 rows, 26 nonzeros
```

Triplets repeat each row number once per nonzero. **Compressed sparse row** form (**CSR**) sorts
the nonzeros by row and stores the row numbers only as boundaries. It keeps three arrays:

- `data`: the nonzero values, row after row;
- `indices`: the column of each value in `data`;
- `indptr` (index pointer): where each row starts in `data`, plus one last entry for where the last
  row ends. Row $`i`$'s nonzeros sit at positions `indptr[i]` up to, but not including,
  `indptr[i + 1]`.

[SciPy](https://docs.scipy.org/doc/scipy/) is Python's library for scientific computing, built on
NumPy. Its module `scipy.sparse` holds sparse matrices; the programs import it with
`from scipy import sparse`. `sparse.coo_array` takes the triplets, and `.tocsr()` converts them to
CSR:

```python
A = sparse.coo_array((vals, (rows, cols)), shape=(len(names), len(tiny.projects))).tocsr()
print("indptr :", A.indptr.tolist())
print("indices:", A.indices.tolist())
print("data   :", A.data.tolist())
print("bytes per entry: data", A.data.itemsize, " indices", A.indices.itemsize, " indptr", A.indptr.itemsize)
```

```text
indptr : [0, 4, 9, 11, 12, 13, 13, 14, 16, 17, 18, 19, 19, 20, 21, 22, 24, 26]
indices: [2, 4, 6, 7, 0, 1, 2, 3, 5, 3, 5, 4, 0, 6, 1, 5, 5, 2, 2, 7, 3, 3, 2, 3, 5, 6]
data   : [980, 250, 290, 580, 2150, 2730, 1490, 2000, 840, 1000, 1130, 250, 2150, 290, 2730, 840, 1130, 980, 1490, 580, 2000, 1000, -1, 1, 1, 1]
bytes per entry: data 8  indices 8  indptr 8
```

`indptr` has 18 entries for 17 rows. The last line is the size of one entry of each array
(`itemsize`, in bytes): each value takes 8 bytes, and so does each column index and each `indptr`
entry, because SciPy stored all three as 64-bit integers here. Reading a row is a slice:

```python
i = names.index("budget_2028")
start, end = A.indptr[i], A.indptr[i + 1]
print(f"row {i} ({names[i]}): positions {start}..{end - 1}")
for j, a in zip(A.indices[start:end], A.data[start:end]):
    print(f"  {tiny.project_ids[j]}: {a}")
```

```text
row 1 (budget_2028): positions 4..8
  P001: 2150
  P002: 2730
  P003: 1490
  P004: 2000
  P006: 840
```

These are exactly the nonzeros of the 2028 row of lesson 1.2.1's matrix. An **empty row** shows
up as two equal neighbours in `indptr`: positions 5 and 6 are both 13, so row 5 (`region_Ridge_2029`)
has no nonzeros, because no Ridge project spends in 2029 when every project starts early.

<!-- practice 1 -->

## Sparse Products Give the Same Answer in a Fraction of the Memory

A CSR matrix supports `A @ x` like a NumPy array. To compute row $`i`$'s activity it only visits
row $`i`$'s nonzeros, `data[indptr[i]:indptr[i+1]]` times the matching entries of $`x`$, and never
the zeros:

```math
(Ax)_i = \sum_{k = \text{indptr}_i}^{\text{indptr}_{i+1} - 1} \text{data}_k \; x_{\text{indices}_k}
```

Here is that product checked against the dense one, for a plan that funds every third project:

```python
A, b, names = csr(generate(size))
dense = A.toarray()
x = np.zeros(A.shape[1], dtype=int)
x[::3] = 1                                     # fund every third project
same = np.array_equal(A @ x, dense @ x)
broken = int(np.sum(A @ x > b))
print(f"{size:6} same activities: {same}, rows broken: {broken} of {A.shape[0]},"
      f" dense {dense.nbytes / 1e6:.1f} MB, CSR {stored_bytes(A) / 1e6:.2f} MB")
if size == "large":
    print(f"       {A.nnz:,} nonzeros and {len(A.indptr):,} indptr entries: CSR {stored_bytes(A):,} bytes,"
          f" dense {dense.nbytes:,} bytes")
```

`size` runs over `"medium"` and `"large"`, and `stored_bytes(A)` is the memory of the CSR form,
shown below.

```text
medium same activities: True, rows broken: 9 of 86, dense 0.3 MB, CSR 0.02 MB
large  same activities: True, rows broken: 142 of 1044, dense 83.5 MB, CSR 0.56 MB
       34,610 nonzeros and 1,045 indptr entries: CSR 562,120 bytes, dense 83,520,000 bytes
```

The answers are identical, entry for entry. The memory is not: on the large portfolio the dense
matrix takes 83.5 MB and the CSR one 0.56 MB, about 150 times less. The CSR size is the bytes of
its three arrays:

```python
def stored_bytes(A: sparse.csr_array) -> int:
    return A.data.nbytes + A.indices.nbytes + A.indptr.nbytes
```

With 8 bytes per entry, as printed above, that is 8 bytes of value and 8 bytes of column index per
nonzero, plus 8 bytes per `indptr` entry. On large: 34,610 nonzeros × 16 bytes + 1,045 `indptr`
entries × 8 bytes = 562,120 bytes, as printed. The dense array holds 8 bytes for every one of its
10,440,000 entries, zeros included: 83,520,000 bytes. So CSR's three arrays grow
with the number of nonzeros (plus one `indptr` entry per row), while a dense matrix grows with rows
times columns. If a model's rows and columns both double while each row keeps its few nonzeros,
the dense matrix quadruples and the CSR one only doubles. Section 11 works at the scales where that
difference decides what fits in memory.

(The plan is not a sensible one; it only gives the product something to multiply.)

<!-- practice 2 -->

## A Solver Receives the Model as Nonzeros, Not as a Grid

OR-Tools' MathOpt, the modeling library of lesson 1.1.3, can export the model it hands to a
solver. Build the tiny model from the CSR rows, one constraint per row, using only each row's
nonzeros (`model` is a `mathopt.Model` and `x` its list of eight binary variables, the must-do P002's
with lower bound 1):

```python
for i, name in enumerate(names):
    start, end = A.indptr[i], A.indptr[i + 1]
    row = mathopt.LinearExpression(sum(float(a) * x[j] for j, a in zip(A.indices[start:end], A.data[start:end])))
    model.add_linear_constraint(expr=row, ub=float(b[i]), name=name)
```

Then ask for the exported model and read its constraint matrix:

```python
proto = model.export_model()                    # the model in MathOpt's exchange format
matrix = proto.linear_constraint_matrix          # its constraint matrix, as triplets
print("export_model() returns a", type(proto).__name__)
print("CSR nonzeros:", A.nnz, " rows:", A.shape[0], " MathOpt constraints:", len(list(model.linear_constraints())))
print("MathOpt matrix:", type(matrix).__name__, "with", len(matrix.coefficients), "entries")
print("row_ids     :", list(matrix.row_ids)[:9])
print("column_ids  :", list(matrix.column_ids)[:9])
print("coefficients:", [int(v) for v in matrix.coefficients][:9])
```

```text
export_model() returns a ModelProto
CSR nonzeros: 26  rows: 17  MathOpt constraints: 17
MathOpt matrix: SparseDoubleMatrixProto with 26 entries
row_ids     : [0, 0, 0, 0, 1, 1, 1, 1, 1]
column_ids  : [2, 4, 6, 7, 0, 1, 2, 3, 5]
coefficients: [980, 250, 290, 580, 2150, 2730, 1490, 2000, 840]
```

`export_model()` returns the model in MathOpt's **exchange format**: a `ModelProto`, a *protocol
buffer*, which is Google's format for structured data that programs in different languages can
pass to each other. It is the complete description `solve` hands to a solver. Its field
`linear_constraint_matrix` is a `SparseDoubleMatrixProto`, a sparse matrix stored as triplets in
three parallel lists: `row_ids`, `column_ids` and `coefficients` (the program prints the first nine
of each). There are 26 of them, the same 26 nonzeros. The 110 zeros of the 17-by-8 grid are not in it, and all 17 rows are, including the
empty `region_Ridge_2029`. `LinearExpression(...)` wraps each sum so that a row with no terms is
still an expression to constrain, not the plain number 0 that `sum` of nothing gives.

So when you write `x[P003] * 980` into a MathOpt constraint, you are adding one triplet. A model
with a million variables is buildable because a typical row mentions a handful of them. This is
also why model-building code should never form a dense row (`sum(A[i, j] * x[j] for j in
range(n))`) when it can loop over a row's nonzeros: the dense loop visits every zero on the way.

How the solver then works on those nonzeros, keeping its own data sparse through every step, is
inside the algorithms of section 2 and is not something this lesson's programs measure.

## The Model

The model of lesson 1.2.1 with regional budgets added (marked), and must-do projects written as
variable bounds rather than rows. Nothing in this lesson solves it; it is built and stored.

**Sets.** $`P`$ the projects; $`Y`$ the years; $`R`$ the regions (Ridge, Valley, Coast, Plains);
$`P_r \subseteq P`$ the projects in region $`r`$; $`M \subseteq P`$ the must-do projects;
$`C \subseteq P`$ the child projects, with parent $`p(c)`$; $`\mathcal{G}`$ the alternative groups.

**Parameters.** $`\text{npv}_j`$ ($k); $`a_{yj}`$, what project $`j`$ spends in year $`y`$ if it
starts in its earliest start year ($k); $`B_y`$, the budget of year $`y`$ ($k); $`B_{r,y}`$, the
budget of region $`r`$ in year $`y`$ ($k).

**Variables.** $`x_j \in \{0, 1\}`$ for $`j \in P \setminus M`$, and $`x_j = 1`$ (lower bound 1)
for $`j \in M`$.

**Objective.**

```math
\max \; \sum_{j \in P} \text{npv}_j\, x_j
```

**Constraints.**

```math
\begin{aligned}
\sum_{j \in P} a_{yj}\, x_j &\le B_y && \forall y \in Y && \text{(budget}_y) \\
\sum_{j \in P_r} a_{yj}\, x_j &\le B_{r,y} && \forall r \in R,\ y \in Y && \text{(region}_{r,y}) \quad \leftarrow \text{this lesson} \\
x_c - x_{p(c)} &\le 0 && \forall c \in C && \text{(parent}_c) \\
\sum_{j \in g} x_j &\le 1 && \forall g \in \mathcal{G} && \text{(alt}_g)
\end{aligned}
```

Rows: $`|Y| + |R|\,|Y| + |C| + |\mathcal{G}|`$, which is 3 + 12 + 1 + 1 = 17 on GridCap tiny and
10 + 40 + 419 + 575 = 1,044 on large.

## Summary

- **Most entries of a model matrix are zero.** Each row is a rule about a few variables, so the
  density falls as the model grows: 0.33% on GridCap large.
- **Store only the nonzeros.** Triplets (row, column, value) are how a model is built; CSR
  (`indptr`, `indices`, `data`) is how it is stored and read row by row.
- **Sparse products give the same answer in a fraction of the memory.** On GridCap large, 0.56 MB
  instead of 83.5 MB, with identical activities.
- **A solver receives the model as nonzeros.** MathOpt's exported constraint matrix is a list of
  triplets, one per nonzero.

## Reference

| Term | Meaning | On GridCap tiny |
| --- | --- | --- |
| Nonzero | An entry of the matrix that is not 0 | 26 of 136 entries |
| Density | nonzeros ÷ (rows × columns) | 19.12% |
| Triplet (COO) | One nonzero as (row, column, value) | `(1, 0, 2150)` |
| `indptr` | Where each row starts in `data`; one entry per row plus one | 18 entries for 17 rows |
| `indices` | Column of each stored value | `[2, 4, 6, 7, 0, ...]` |
| `data` | The stored values, row by row | `[980, 250, 290, ...]` |
| Empty row | `indptr[i] == indptr[i + 1]` | row 5, `region_Ridge_2029` |

| SciPy | Does |
| --- | --- |
| `sparse.coo_array((vals, (rows, cols)), shape=...)` | A matrix from triplets |
| `.tocsr()` | Converts to CSR |
| `A.nnz`, `A.shape` | Number of nonzeros; rows and columns |
| `A.data.itemsize`, `A.data.nbytes` | Bytes per stored entry; bytes of the whole array |
| `A @ x` | Activities, visiting nonzeros only |
| `A.toarray()` | The dense NumPy array (only for small matrices) |

**Further reading:** [MathOpt (OR-Tools)](https://developers.google.com/optimization/math_opt) (what a MathOpt model can hold and the solvers it is handed to); [MathOpt `model.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/model.proto) (the `ModelProto` that `export_model()` returns, which keeps linear constraints in a struct-of-arrays form); [MathOpt `sparse_containers.proto`](https://github.com/google/or-tools/blob/stable/ortools/math_opt/sparse_containers.proto) (`SparseDoubleMatrixProto`: triplets in row-major order, each (row, column) pair at most once); [SciPy sparse arrays](https://docs.scipy.org/doc/scipy/reference/sparse.html) (build in COO, convert to CSR for arithmetic, and the move from sparse matrices to sparse arrays); [SciPy `csr_array`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_array.html) (the `data`, `indices`, `indptr` layout, and duplicate triplets summed on conversion).

## Challenges

1. Add one row per project that says "fund it at most once" ($`x_j \le 1`$). How many nonzeros
   and how much density does the large matrix get? Is such a row worth having?
2. The medium matrix has 86 rows. Without running anything, how many entries does its `indptr`
   have?
3. A colleague builds each constraint as `sum(A[i, j] * x[j] for j in range(n))` over the dense
   large matrix. How many terms does that visit in total, and how many are zero?

## Design Note: Build Sparse From the Start

It is tempting to build $`A`$ as a NumPy array first, because indexing `A[r, j]` is easy, and
convert at the end. On GridCap large that first array is 83.5 MB for 0.56 MB of information, and
on the models of section 11 it would not fit at all. Build the triplets as the rules are written,
as `model_matrix.py` does, and convert to CSR once. MathOpt does the same: every term you add to a
constraint is one triplet, and nothing ever forms the grid.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy of the code, so the course's own files never change.

**density.py.** Counts rows, columns, nonzeros and memory for every GridCap size (*Most Entries of a Model Matrix Are Zero*). *Try:* Leave the region rows out of `model_matrix.py`. Predict how the large density changes.

- Program: [density.py](src/density.py)

**nonzeros_per_row.py.** Nonzeros per row, by kind of row, on the large portfolio (*Most Entries of a Model Matrix Are Zero*). *Try:* Run it on `medium`. Which kind of row changes most?

- Program: [nonzeros_per_row.py](src/nonzeros_per_row.py)

**csr_anatomy.py.** The tiny matrix as triplets, then as CSR's three arrays, and one row read back (*Store Only the Nonzeros*). *Try:* Read back `alt_G006` instead of `budget_2028`. Predict its positions in `data`.

- Program: [csr_anatomy.py](src/csr_anatomy.py)

**sparse_product.py.** The CSR product against the dense one, with memory (*Sparse Products Give the Same Answer*). *Try:* Fund every second project instead of every third. Predict whether more or fewer rows break.

- Program: [sparse_product.py](src/sparse_product.py)

**mathopt_matrix.py.** Builds the tiny model in MathOpt from the CSR rows and prints the triplets MathOpt exports (*A Solver Receives the Model as Nonzeros*). *Try:* Add the term `0 * x[0]` to the first row. Does the exported matrix grow?

- Program: [mathopt_matrix.py](src/mathopt_matrix.py)

**model_matrix.py.** Builds GridCap's model matrix as triplets and converts it to CSR; every program of this lesson imports it.

- Library: [model_matrix.py](src/model_matrix.py)
