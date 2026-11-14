"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import tempfile

from snapshot import Edited, Store, canonical, digest

snap = {"years": [2031, 2032], "rate": 0.0375, "budget": {2031: 500, 2032: 450},
        "projects": {"P7": {"cost": [80], "must": False}}}
same = {"projects": {"P7": {"must": False, "cost": [80]}}, "budget": {2032: 450, 2031: 500},
        "rate": 0.03750000004, "years": [2031, 2032]}

print("canonical bytes:", canonical(snap))
print("digest:", digest(snap))
print("digest of reordered copy:", digest(same))

with tempfile.TemporaryDirectory() as root:
    store = Store(root)
    key = store.put(snap)
    print("read back:", store.get(key))
    (store.root / f"{key}.json").write_bytes(canonical({**snap, "rate": 0.04}))
    try:
        store.get(key)
        print("edited file read: no error")
    except Edited as error:
        print("edited file read:", error)
