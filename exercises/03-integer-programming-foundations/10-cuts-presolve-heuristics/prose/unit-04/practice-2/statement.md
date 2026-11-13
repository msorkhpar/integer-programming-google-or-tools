The planners want to know which of HiGHS's heuristics earn their keep on GridCap's models. From the
parsed progress rows of a log, list every new incumbent with the source that found it.

Write `history(rows)` in `sources.py`. `rows` is a list of dicts with at least the keys `src` (a
letter, or `""` on a periodic row), `bound` and `incumbent` (floats; `bound` may be
`float("inf")`), in log order. Return a list with one tuple `(name, incumbent, gap)` for every row
whose `src` is not empty, in order, where `name` is `LEGEND[src]` (the dict in the starter, copied
from HiGHS's legend; upper and lower case are different letters) and

```math
\text{gap} = \frac{\lvert \text{bound} - \text{incumbent} \rvert}{\lvert \text{incumbent} \rvert}
```

or `None` when the bound is infinite. The same formula serves a maximization (bound above the
incumbent) and a minimization (bound below it).
