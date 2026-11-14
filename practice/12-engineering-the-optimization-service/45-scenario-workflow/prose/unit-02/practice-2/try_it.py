"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from replay import in_force


def entry(seq, action, project="", kind="", year=None):
    return {"seq": seq, "action": action, "project": project, "kind": kind, "year": year,
            "by": "planner-x", "why": "review"}


trail = [entry(4, "set", "P-5", "start_in", 2033), entry(1, "set", "P-5", "start_in", 2031),
         entry(2, "set", "P-9", "out"), entry(3, "revoke", "P-9", "out")]
print("four entries:", in_force(trail))
print("plus an inherit at seq 5:", in_force(trail + [entry(5, "inherit", "P-2", "out")]))
print("plus a clear at seq 6 and a set at seq 7:",
      in_force(trail + [entry(6, "clear"), entry(7, "set", "P-1", "start_in", 2032)]))
