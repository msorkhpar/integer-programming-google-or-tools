"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from roster import named_conflict

nurses = ["Dee", "Eli", "Fay", "Gus"]
loose = {"Dee": 2, "Eli": 2, "Fay": 2, "Gus": 2}

print("conflict, need 2/2/2:", named_conflict(nurses, {1: 2, 2: 2, 3: 2}, loose, []))
print("conflict, need 5 on day 1:", named_conflict(nurses, {1: 5, 2: 2, 3: 2}, loose, []))
print("conflict, need 3 on day 2, Dee and Eli off:",
      named_conflict(nurses, {1: 2, 2: 3, 3: 2}, loose, [("Dee", 2), ("Eli", 2)]))
