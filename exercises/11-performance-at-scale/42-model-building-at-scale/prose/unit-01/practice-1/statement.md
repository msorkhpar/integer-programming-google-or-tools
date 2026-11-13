GridCap's model builds run on a shared test server, where other jobs come and go. Last week a
rewrite of the budget rows was declared "three times faster" from one timing of the old builder on
Monday and one of the new builder on Tuesday. Nobody could repeat it. The team wants a function
that compares two builders fairly, on a busy machine, in one process.

Write `speedup(old, new, rounds, warmup, clock)` in `compare.py`. `old` and `new` are functions that
take no arguments (each builds a model); `clock` is a function that returns the current time in
seconds, `time.perf_counter` by default. The function returns how many times faster `new` is than
`old`, measured this way:

- first, `warmup` untimed runs of each builder, `old` then `new`, so one-time costs do not count;
- then `rounds` rounds; each round times one run of `old` and then one run of `new`, each between
  two readings of `clock`, and computes the round's ratio, old's time divided by new's time;
- the answer is the median of the round ratios (with an even number of rounds, the mean of the
  two middle ones).

A slow patch on the machine then hits both builders of the same round, and their ratio survives
it. The tests pass a fake clock that moves only when a builder runs, so your function must read
the clock only around each timed run; the given helper `timed(work, clock)` does exactly that for
one run. Run the file to measure two toy functions on your machine. About five lines.
