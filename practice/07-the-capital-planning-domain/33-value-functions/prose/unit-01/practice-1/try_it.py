"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from outages import Step, indices

storm = [Step(300, 3), Step(900, 45), Step(300, 120)]
fault = [Step(500, 25)]

print("storm only, 20000 served:", indices([storm], 20_000))
print("storm and fault, 20000 served:", indices([storm, fault], 20_000))
print("a 3-minute blip, 20000 served:", indices([[Step(1_000, 3)]], 20_000))
