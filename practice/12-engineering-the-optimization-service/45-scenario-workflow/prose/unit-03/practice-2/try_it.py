"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from store import Store

store = Store()
print("create B-7:", store.create("B-7", {"bridges": 120, "tunnels": 80}))
mine, v_mine = store.read("B-7")
theirs, v_theirs = store.read("B-7")
mine["bridges"] = 90
theirs["tunnels"] = 60
print("save mine from version", v_mine, "->", store.save("B-7", v_mine, mine))
print("save theirs from version", v_theirs, "->", store.save("B-7", v_theirs, theirs))
mine["bridges"] = 0
print("stored now:", store.read("B-7"))
