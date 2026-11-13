A city water utility (a fictional one) collects capital requests from three programs: water
mains, treatment plants and meters. Each request starts in a year and spends a profile of amounts
($k) in that year and the following ones. Finance has already set an **envelope** for some
programs and years: the most that program may spend that year. Before anything is selected, the
capital planning team wants to see where the requests already break an envelope.

Write two functions in `envelopes.py`:

- `requested_by_year(requests, programs, years)`: for every program in `programs` and every year
  in `years`, what the requests would spend there if all were funded as asked. Every program and
  year appears, with 0 where nothing is asked. Spend in a year outside `years` is left out.
- `oversubscribed(requests, envelopes)`: one tuple `(program, year, requested, excess)` for every
  envelope that the requests exceed, with `excess` the amount above the envelope, sorted by
  program and then year. An envelope met exactly is not exceeded.

A request for a program not in `programs` (or with no envelope) is left out. Before you code, take a
request that starts in 2027 with the profile (500, 300, 100) and write down what it adds to 2027,
2028 and 2029. The tests use small hand-made request lists. About fifteen lines.
