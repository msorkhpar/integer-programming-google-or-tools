"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from feeders import Feeder, consequence, saidi_minutes

plain = Feeder(1_500, 0, 0.0, 2.0, 6.0, 0.025, 0.6, 90)
mixed = Feeder(1_200, 25, 0.0, 2.0, 6.0, 0.025, 0.6, 90)
switched = Feeder(1_200, 25, 0.5, 2.0, 6.0, 0.025, 0.6, 90)

for name, f in (("1500 residential", plain), ("1200 + 25 critical", mixed), ("same, half switched", switched)):
    print(f"{name}: cost {consequence(f):.2f}, SAIDI minutes of 60000 {saidi_minutes(f, 60_000):.3f}")
