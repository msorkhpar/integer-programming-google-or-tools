"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from fleet import carry_forward, committed

old = {"V1": 2030, "V2": 2032, "V3": 2031, "V4": 2034}
windows = {"V2": [2031, 2032], "V3": [2031, 2032, 2033], "V4": [2031, 2032], "V7": [2031]}

print("committed in 2030:", committed(old, 2030))
start = carry_forward(old, windows, 2030)
for key, value in start.items():
    print(f"start for {key}:", value)
