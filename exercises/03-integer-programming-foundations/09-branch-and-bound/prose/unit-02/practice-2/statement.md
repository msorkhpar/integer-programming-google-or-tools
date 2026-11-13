The warehouse-siting search prints a progress line after every node, so the planners can see how
close it is to done. Each line needs the range the optimum must lie in.

Write `optimum_range(incumbent, waiting, tol=1e-6)` in `optimum_range.py`. `incumbent` is the best
plan's value so far (`None` before the first plan); `waiting` is the list of bounds carried by the
nodes still waiting to be solved (each one its parent's LP value). Return `(low, high, proven)`:

```math
\text{low} = \underline{z}, \qquad
\text{high} = \max\big(\underline{z},\ \max_{n \in \text{waiting}} \text{bound}(n)\big), \qquad
\text{proven} = (\text{high} - \text{low} \le \text{tol})
```

With no incumbent, `low` is `None`, `high` is the largest waiting bound, and `proven` is `False`.
With no incumbent and nothing waiting, return `(None, None, False)`. The problem is a maximization.
