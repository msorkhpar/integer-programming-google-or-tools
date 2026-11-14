"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from incumbents import in_hand, work_to_first, work_to_within

log = [(8.0, 7300.0), (25.0, 7050.0), (60.0, 7120.0), (210.0, 6700.0), (700.0, 6650.0)]

print("work to the first plan:", work_to_first(log))
print("work to within 1% of 6650:", work_to_within(log, 6650.0, 0.01))
print("plan in hand after 100 work:", in_hand(log, 100.0))
print("plan in hand after 5 work:", in_hand(log, 5.0))
print("work to the first plan, empty log:", work_to_first([]))
