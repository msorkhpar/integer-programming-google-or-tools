A school district compares options for its bus routes. Each option is scored on several measures;
some are better high (students served, on-time rate) and some better low (cost, longest ride). Before
anyone argues about weights, the district wants the list cut down to the options worth arguing
about: those that no other option beats.

Write `unbeaten(options, senses)` in `pareto.py`. `options` maps each option's name to its tuple of
measures, and `senses[m]` is `"max"` or `"min"` for measure `m`. Return the names of the options
that no other option dominates, in the sense of the lesson: at least as good in every measure and
strictly better in at least one. The helper `dominates(p, q, senses)` is there for you to fill in
and use.

Before coding, decide what your function should do with two options whose measures are all equal,
and with an option that ties another on one measure and loses on the other; then check your
decision against the definition.

About twelve lines.
