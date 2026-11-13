A distribution utility (fictional) wants a test portfolio of feeders for its performance work, from
a few hundred up to 100,000. Each feeder has a length (1 to 40 km), a number of customers (50 to
5,000) and the crew-days its inspection takes (2 to 20). The data will be pinned by a hash in tests
and grown over time, so the generator has to keep four promises:

- **reproducible:** the same `n` and seed give the same feeders, also in a new Python process whose
  `PYTHONHASHSEED` differs;
- **prefix-stable:** the first 10 feeders of a 1,000-feeder portfolio are the 10-feeder portfolio of
  the same seed;
- **seeds do not overlap:** seed 8 is not seed 7 shifted by one feeder;
- **every value in range**, ids numbered `F00001`, `F00002`, ... in order.

Write `generate_feeders(n, seed)` in `feeders.py`, returning a list of `Feeder`. The helper
`between(draw, low, high)` turns one `random()` draw of a `random.Random` into a whole number from
`low` to `high`. Use only `random.Random` and its `random()` method (through `between`), as GridCap
does, so the numbers stay the same across Python versions. The ranges allow fewer than a million
feeders. About six lines.
