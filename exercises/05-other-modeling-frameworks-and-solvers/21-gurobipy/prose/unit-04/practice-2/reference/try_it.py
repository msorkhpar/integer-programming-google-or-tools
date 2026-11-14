"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from masking import mask_line

# Made-up solver messages.
messages = [
    "No license found (user pat, host bench-3, cores 4)",
    "License issued to jane.doe@example.invalid until May",
    "key 0a1b2c3d-4e5f-6a7b-8c9d-0e1f2a3b4c5d expired",
    "Model has 812 rows and 1,040 columns",
]
for message in messages:
    print(f"{message!r} ->", mask_line(message))
