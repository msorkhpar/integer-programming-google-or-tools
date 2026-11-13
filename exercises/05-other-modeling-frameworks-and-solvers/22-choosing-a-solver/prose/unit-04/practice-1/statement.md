A team ran its benchmark harness several times on the same machine and kept, for each repetition,
each solver's shifted geometric mean of wall seconds. The numbers move from run to run, so the team
adopts a rule for its recommendation memo: a solver may be called faster only if it is ahead **by at
least a stated factor on every repetition**.

Write `faster(a, b, factor)` in `claim.py`. `a[k]` and `b[k]` are the two solvers' wall-clock means
in repetition `k` (positive numbers, same length). Return `"a"` if `b[k] / a[k] >= factor` for every
`k`, `"b"` if `a[k] / b[k] >= factor` for every `k`, and `"neither"` otherwise. The factor is
greater than 1.

About four lines.
