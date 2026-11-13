A small utility's planning service (fictional, like its practice portfolio) is about to put its
plans in front of a regulator. The regulator's first question is whether the same inputs always give
the same plan. Your milestone answers it with evidence: every run writes a **manifest**, and a
**harness** reruns one configuration in fresh processes and compares the manifests byte for byte.

`run_harness.py` gives you the practice portfolio `SNAPSHOT` (a reduced rule set: must-do and
at-most-once rows and yearly budgets), `snapshot_for(config)`, which applies a config's budget
overrides, and `solve(snapshot, objective, order, seed)`, a CP-SAT solve on one worker. A config is a
dict such as `{"objective": "npv"}`, `{"objective": "count", "order": "set"}` or
`{"objective": "npv", "budget": {"2028": 200}}`. A config may also give a `"seed"`. A key the config
leaves out takes its default: `objective` `"npv"`, `order` `"sorted"`, `seed` 0. The seed is passed to
`solve` and recorded as the manifest's `random_seed`; it is CP-SAT's seed, not the child process's
`PYTHONHASHSEED`. The bottom of the file already runs one config
given on the command line and prints its manifest's canonical bytes: that is the child process.

Write:

| function | contract | lesson |
| --- | --- | --- |
| `canonical(obj)` | one byte string per value: sorted keys at every level, no spaces, ASCII only | 10.2.4 |
| `manifest(config)` | a dict with four sections: `inputs` (`snapshot`: the SHA-256 hex digest of the canonical bytes of the data the run solved, budget overrides included; `objective`; `order`), `solver` (`name` "CP-SAT", `num_workers` 1, `random_seed`), `versions` (`python`, `ortools`), `result` (`status`, `objective`, `plan` as a sorted list of `[project, year]` pairs, `branches`, `conflicts`). No clock reading, and nothing that names a machine or a person | 10.2.4 |
| `differences(a, b)` | the dotted paths (`"result.plan"`) at which two manifests differ, sorted; a list is compared whole | 10.2.5 |
| `run_in_child(config, seed)` | run this file with `json.dumps(config)` as its argument in a fresh `sys.executable` process whose `PYTHONHASHSEED` is `seed`; return its standard output as bytes | 10.2.5 |
| `harness(config, runs=10)` | run the config in `runs` children with seeds 1 to `runs`; if any output differs from the first, raise `NotDeterministic` with a message that names the run and every differing path; otherwise return the SHA-256 hex digest of the manifest bytes | 10.2.5, 12.3.4 |

The harness must be able to fail: the tests run `{"objective": "count", "order": "set"}`, a question
with many tied plans whose model is built in a set's order, and expect `NotDeterministic` naming
`result.plan`. About forty lines.
