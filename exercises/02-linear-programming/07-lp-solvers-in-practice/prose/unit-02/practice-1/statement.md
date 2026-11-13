A pumping-station operator runs its energy LP every night on HiGHS and keeps only the log. Their
monitoring script needs the verdict from it: how the run ended, how much work it did, and the
objective, but only when the objective is an answer.

Write `read_footer(log)` in `footer.py`. `log` is the list of lines a HiGHS solve wrote. Return a
dict with three keys:

- `"status"`: the text after `Model status` (`"Optimal"`, `"Infeasible"`, `"Unbounded"`, ...).
- `"iterations"`: a dict from the kind of iteration to its count, read from each footer line
  ending in `iterations`, keyed by the line's first word: `Simplex   iterations: 7` gives
  `{"Simplex": 7}`. A run with no such line gives `{}`.
- `"objective"`: the number after `Objective value` as a float when the status is `"Optimal"`,
  and `None` for any other status, even though HiGHS prints the line anyway.

The footer's labels are padded with spaces to line up their colons, so split each line at its
first `:` and strip both sides, rather than matching exact spacing. Lines without a `:` are
skipped.
