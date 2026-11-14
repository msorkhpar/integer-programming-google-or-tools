"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from progress import events, stopped_by_a_limit

# Made-up progress lines of a delivery-rostering model (minimized), shaped like CP-SAT's.
log = """#Bound   0.01s best:inf   next:[120,2400] initial_domain
#1       0.04s best:1900 next:[120,1899] main
#Bound   0.07s best:1900 next:[640,1899] main (probing)
#2       0.11s best:980 next:[640,979] main
#Done    0.20s main
"""
for event in events(log):
    print("event:", event)
print("stopped by a limit (full log):", stopped_by_a_limit(log))
print("stopped by a limit (first 3 lines):", stopped_by_a_limit("\n".join(log.splitlines()[:3])))
