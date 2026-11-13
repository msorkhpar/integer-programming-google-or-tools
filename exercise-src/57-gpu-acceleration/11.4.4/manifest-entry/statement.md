A water utility's optimisation service writes a manifest entry for every solve, and its runs now
happen on CPUs and on a GPU, with HiGHS, OR-Tools and cuOpt. The auditors need each entry to say
what was promised, and to name nothing that identifies a machine.

Write `entry(settings, result, device)` in `manifest.py`. `settings` holds the `solver`, `method`,
`tolerance` and `threads` the service asked for; `result` is what the solver returned (it may hold
more than the manifest should); `device` is where the solve ran: `{"device": "cpu"}`, or a GPU
report with `"device": "gpu"`, the card's `name`, `driver_cuda`, `cuda_runtime` and other fields,
some of which identify one card. Return:

- a `"solver"` block with the keys `name` (the solver's name, from `settings["solver"]`),
  `method`, `tolerance`, `threads` and `device`; for a GPU also `device_name` (the card's model),
  `driver_cuda` and `cuda_runtime`, and nothing else from the report;
- when the method asked for is `"concurrent"`, the block's `method` is the one that won
  (`result["solved_by"]`), and the block also holds the key `requested` with the value
  `"concurrent"` (inside the `"solver"` block, not beside it); with no winner in the result, return
  None instead of an entry. A run that is not concurrent has no `requested` key;
- a `"result"` block with only `status`, `objective`, `x_digest` and `iterations` (those present).

About fifteen lines.
