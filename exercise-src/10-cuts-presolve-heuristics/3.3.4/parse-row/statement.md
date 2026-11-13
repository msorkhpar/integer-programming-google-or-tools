GridCap's nightly job keeps the HiGHS log of every run, and the planners want a chart of the bound
and the incumbent over the search. The first step is reading one line of the progress table.

Write `parse_row(line)` in `rows.py`. A progress row is a line whose first character is a space,
whose second character is the source letter or a space, and whose remainder, split on whitespace,
has exactly 12 fields:

| Field | Proc. | InQueue | Leaves | Expl. | BestBound | BestSol | Gap | Cuts | InLp | Confl. | LpIters | Time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Example | `0` | `0` | `0` | `0.00%` | `275164.826811` | `271757` | `1.25%` | `0` | `0` | `0` | `16` | `0.1s` |

where Proc. is a whole number and Expl. ends in `%`. For a progress row, return a dict with the keys
`src` (the letter, or `""` for a blank), `nodes` (Proc., an `int`), `bound` and `incumbent` (BestBound
and BestSol as `float`; the text `inf` is `float("inf")`), `gap` (the Gap as a fraction, so `1.25%`
is `0.0125`, or `None` when the log prints `Large`), `cuts` and `lp_iters` (`int`). For any other
line, return `None`.

How strict to be: the reference solution checks exactly four things, the leading space, the 12
fields, Proc. made only of digits, and Expl. ending in `%`, and nothing else. It takes any character
in the second position as the source letter (a letter it has never seen, say `Q`, is still a row),
and it does not check the other fields beyond converting them: on a real HiGHS row they are always
numbers, `inf` or `Large`. The tests never pass a line that clears the four checks and then fails a
conversion.
