"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from devices import Device, augmented_choice

clinic = [Device("Scanner", 90, 3, 50), Device("Oxygen", 70, 8, 30),
          Device("Lift", 50, 2, 20), Device("Sterilizer", 0, 6, 10)]

for floor in (0, 10, 16, 30):
    print(f"budget 90, at least {floor} safety:", augmented_choice(clinic, 90, floor, span=19))
