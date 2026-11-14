"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from libraries import Upgrade, frontier

branches = [Upgrade("Riverside", 10, 15, 30), Upgrade("Castle", 18, 4, 30),
            Upgrade("Fenn", 5, 25, 25), Upgrade("Moor", 8, 10, 15)]

print("budget 60:", frontier(branches, 60))
print("budget 30:", frontier(branches, 30))
