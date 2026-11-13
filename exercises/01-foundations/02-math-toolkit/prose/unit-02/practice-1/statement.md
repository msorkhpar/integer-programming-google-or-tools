A water utility's model builder adds terms to its rules one at a time, as (row, column, value)
triplets: row is the pumping station's rule, column the pump, value the coefficient. Before the
matrix goes to the checker it is compressed into CSR form, and you write the compressor, with no
SciPy.

Write `to_csr(n_rows, triplets)` in `csr.py`. It returns three lists, `(indptr, indices, data)`:

- `data`: the values, row 0 first, then row 1, and so on; within a row, by increasing column;
- `indices`: the column of each value in `data`;
- `indptr`: `n_rows + 1` entries; row $`i`$'s values are `data[indptr[i]:indptr[i + 1]]`, so
  `indptr[0]` is 0 and the last entry is `len(data)`.

The triplets may arrive in any order. A row may have no triplets at all, including the last rows.
When two triplets name the same row and column, the builder meant their sum: store one entry with
the two values added.

About ten lines.
