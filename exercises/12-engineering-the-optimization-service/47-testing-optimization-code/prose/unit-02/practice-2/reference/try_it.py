"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from hypothesis import given, settings

from water_strategy import instances

drawn = []


@settings(max_examples=4, derandomize=True, database=None, deadline=None)
@given(instances())
def collect(instance):
    drawn.append(instance)


collect()
for n, instance in enumerate(drawn[:4], 1):
    print(f"instance {n}: budget {instance['budget']}, must {instance['must']}, needs {instance['needs']}")
