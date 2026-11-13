A telecom operator plans tower upgrades with a nightly MILP. Each run leaves a record like

```python
{"inputs_digest": "9f2c...", "solver": "highs", "params": {"random_seed": 3, "node_limit": 500},
 "versions": {"ortools": "9.15.6755", "python": "3.14.7"},
 "status": "OPTIMAL", "objective": 812.0, "plan": {"TW-12": 2027, "TW-04": 2028},
 "started_at": "2026-11-11T02:00:03", "wall_seconds": 41.7, "host": "batch-node-7"}
```

The operator's harness compares runs by their manifest bytes. Write `manifest_bytes(record)` that
returns those bytes: everything a rerun of the same inputs on the same software must reproduce, in
one canonical JSON form, and nothing that a rerun need not reproduce or that names the machine.

About six lines.
