A crew-rostering service maximizes a score with CP-SAT and wants a chart of each solve's
progress. The log's progress lines look like this:

```
#Bound   0.02s best:-inf  next:[300,5200] main
#1       0.03s best:4100 next:[4101,5200] main
#Done    0.09s main
```

`#1`, `#2`, ... announce a new plan, `#Bound` a better bound, and `#Done` the end of the search.
After the time come `best:` (the best plan's value, `-inf` before any plan exists), `next:[low,high]`
(for a maximization, `high` is the bound) and the worker that caused the event, sometimes followed
by a comment. `#Model` lines report model changes and are not progress events.

Write two functions in `progress.py`:

- `events(log)`: a list with one tuple `(kind, best, bound, worker)` per `#N`, `#Bound` and `#Done`
  line, in order. `kind` is `"solution"`, `"bound"` or `"done"`; `best` and `bound` are integers,
  or `None` when the line has no number for them (`-inf`, or a `#Done` line); `worker` is the
  worker's name alone.
- `stopped_by_a_limit(log)`: `True` if the log has no `#Done` line.

A `#Done` line has no `best:` or `next:` part, so a pattern for the range, such as the lesson's
`RANGE`, does not match it. Read such a line's worker as the first word after the time, as the
reference does (`rest.split()[0]` on what follows the time, or `""` if nothing follows), and give
it `None` for `best` and `bound`.

Skip every other line. About fifteen lines.
