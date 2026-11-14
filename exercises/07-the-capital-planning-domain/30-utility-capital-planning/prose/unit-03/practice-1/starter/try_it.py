"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from snapshot import changed_fields, snapshot_id

a = {"budget": {"2031": 640}, "force_in": ["P9", "P2"], "force_out": ["P5"], "settings": {"gap": 0.0}}
b = {"settings": {"gap": 0.0}, "force_out": ["P5"], "force_in": ["P2", "P9"], "budget": {"2031": 640}}
c = {**a, "budget": {"2031": 600}, "force_out": []}

print("id of a:", snapshot_id(a))
print("id of b:", snapshot_id(b))
print("id of c:", snapshot_id(c))
print("fields changed a -> c:", changed_fields(a, c))
