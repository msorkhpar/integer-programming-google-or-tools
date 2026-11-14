"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pumps import mean_remaining_life

for age in (0, 15, 35, 60):
    print(f"age {age}, beta 3, eta 50:", round(mean_remaining_life(age, 3.0, 50.0), 3))
print("age 20, beta 1, eta 50:", round(mean_remaining_life(20, 1.0, 50.0), 3))
