An operations-research team (not GridCap) gets problem statements from many departments and wants
the first triage done the same way every time. Each statement has been read into a `Problem`, a
record of yes/no facts, given in `chooser.py`:

| Field | True when |
| --- | --- |
| `routes` | the decisions are vehicles' routes between places |
| `shape` | the problem is an `"assignment"`, a `"flow"` or a `"knapsack"`; `None` if none of these |
| `side_rules` | it has a rule that its shape's special solver cannot take |
| `continuous` | some amount may be fractional |
| `needs_duals` | the caller wants dual prices (shadow prices, reduced costs) |
| `intervals` | it has tasks with start times and durations that may not overlap |
| `logic` | it has many if-then, either-or or sequencing rules |

Write `choose_api(problem)`. It returns one of `"routing"`, `"graph"`, `"knapsack"`, `"CP-SAT"` or
`"MathOpt"`, by lesson 4.1.3's procedure: ask its five questions in order, and the first that says
yes decides. An assignment or a flow goes to `"graph"`. About ten lines.
