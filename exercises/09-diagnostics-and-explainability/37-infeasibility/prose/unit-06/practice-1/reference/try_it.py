"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from messages import translate

jobs = {"A4": "Oak Avenue", "B9": "Quay Street"}
caps = {2030: 15200}
crews = {("upper_valley", 2030): 1}

rows = ["need_A4", "pin_B9_2030", "cap_2030", "before_A4_B9", "crew_upper_valley_2030", "need_Z1", "fog_A4"]
for row, text in zip(rows, translate(rows, jobs, caps, crews)):
    print(f"{row}:", text)
