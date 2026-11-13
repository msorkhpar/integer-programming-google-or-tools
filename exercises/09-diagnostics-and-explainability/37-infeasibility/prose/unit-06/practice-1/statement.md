A city's road-resurfacing model names its rows like this, and its conflict finder returns a list
of such names. The council's planners want each one as a sentence. The table gives the exact
sentence for each kind of row:

| Row name | Sentence |
| --- | --- |
| `cap_2027` | `The 2027 resurfacing budget is $12,500k.` |
| `need_R12` | `R12 Elm Street must be done this plan.` |
| `pin_R31_2027` | `Council fixed R31 Harbour Road to 2027.` |
| `crew_north_2027` | `The north district has 3 paving crews in 2027.` |
| `before_R07_R12` | `R07 Mill Lane must finish before R12 Elm Street starts.` |
| any other name, such as `noise_R12_night` | `Rule noise_R12_night has no description yet.` |

A district with one crew gets the singular: `The west district has 1 paving crew in 2029.` A row of
a known kind that names a job, year or district missing from the data (`need_R99` when `jobs` has
no `R99`) gets the same fallback sentence as an unknown kind: `Rule need_R99 has no description yet.`

`jobs` maps a job id (letters and digits, no underscores) to its street; `caps` maps a year to the
resurfacing budget in $k, written with a thousands separator; `crews` maps `(district, year)` to
the number of paving crews. A district name may contain underscores (`south_east`); in the sentence
each underscore becomes a space.

Write `translate(conflict, jobs, caps, crews)` returning the sentences, in the conflict's order. The
`sentence` helper is a good place for the per-row work. About twenty lines.
