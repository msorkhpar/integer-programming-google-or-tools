"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from relays import trigger_age

for rate in (0.02, 0.08, 0.15):
    age = trigger_age(rate, 2.5, 35.0)
    print(f"rate {rate}, beta 2.5, eta 35:", round(age, 3))
print("rate 0.08, beta 1.0, eta 35:", trigger_age(0.08, 1.0, 35.0))
print("rate 0.08, beta 0.8, eta 35:", trigger_age(0.08, 0.8, 35.0))
