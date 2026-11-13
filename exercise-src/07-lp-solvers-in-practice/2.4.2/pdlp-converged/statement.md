A team runs a very large transport LP with PDLP and wants to know, from the log alone, how many
iterations a tighter or looser tolerance would have needed, without solving again. PDLP's log
reports its progress as a table: each row starts with the iteration number, and the block between
the first and second `|` holds three relative measures, `rel_prim_res`, `rel_dual_res` and
`rel_gap`.

Write two functions in `converged.py`:

- `table_rows(log)` returns every progress row as a tuple
  `(iteration, rel_prim_res, rel_dual_res, rel_gap)`, in log order. A progress row is a line
  whose text before the first `|` starts with a whole number; the header row (` iter# ...`) and
  every other line are skipped. The final-stats row at the end of a log is a progress row too.
- `converged_at(log, tol)` returns the iteration of the first progress row where all three
  measures are within `tol`: $`\text{rel\_prim\_res} \le tol`$, $`\text{rel\_dual\_res} \le tol`$
  and $`|\text{rel\_gap}| \le tol`$. The gap is signed, and it is its size that has to be small.
  If no row gets there, return `None`.
