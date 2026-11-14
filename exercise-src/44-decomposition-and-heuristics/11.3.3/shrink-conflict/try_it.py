"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from shrink import shrink

# A set of jobs is refused when it holds both "paint" and "weld", or all of "lift", "crane", "mast".
def fits(jobs):
    s = set(jobs)
    return not ({"paint", "weld"} <= s or {"lift", "crane", "mast"} <= s)

print("core of paint, sand, weld:", shrink(["paint", "sand", "weld"], fits))
print("core of lift, crane, sand, mast:", shrink(["lift", "crane", "sand", "mast"], fits))
print("core of all six:", shrink(["sand", "paint", "lift", "crane", "weld", "mast"], fits))
