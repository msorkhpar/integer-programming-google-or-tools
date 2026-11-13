A warehouse's planning service keeps its capacity rules in CSR form, because most orders touch
only a few aisles. A dashboard needs each rule's activity for a plan, and the service must never
build the dense matrix to get it.

Write `csr_activity(indptr, indices, data, x)` in `activity.py`. The matrix is in CSR form: row
$`i`$'s values are `data[indptr[i]:indptr[i + 1]]`, and `indices` holds the column of each value.
`x` has one entry per column. Return a list with one number per row, the row's activity:

```math
(Ax)_i = \sum_{k = \text{indptr}_i}^{\text{indptr}_{i+1} - 1} \text{data}_k \; x_{\text{indices}_k}
```

A row with no entries has activity 0. Visit only the stored values: no dense matrix, no NumPy.

About five lines.
