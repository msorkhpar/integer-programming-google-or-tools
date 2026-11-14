"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from children import children

node = {"open_depot": (0, 1), "vans": (0, 12), "shift": (-3, 3)}
print("node:", node)
down, up = children(node, "vans", 5.3)
print("split vans at 5.3, down:", down)
print("split vans at 5.3, up:", up)
down, up = children(node, "shift", -0.6)
print("split shift at -0.6, down:", down["shift"], "up:", up["shift"])
print("node after the splits:", node)
