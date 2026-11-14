"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from tower_manifest import manifest_bytes

record = {"inputs_digest": "a17b03", "solver": "highs", "params": {"random_seed": 5},
          "versions": {"ortools": "9.0"}, "status": "OPTIMAL", "objective": 455.0,
          "plan": {"TX-3": 2031, "TX-1": 2030},
          "started_at": "2030-01-05T03:10:00", "wall_seconds": 12.9, "host": "node-a"}

print("manifest:", manifest_bytes(record))
print("same run, other clock and host:",
      manifest_bytes({**record, "started_at": "2030-01-06T03:11:00", "wall_seconds": 13.4, "host": "node-b"})
      == manifest_bytes(record))
print("same run, objective 450:", manifest_bytes({**record, "objective": 450.0}) == manifest_bytes(record))
