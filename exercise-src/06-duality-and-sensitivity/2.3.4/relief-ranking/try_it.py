"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from relief import worth_buying

offers = [
    {"name": "overtime", "price": 0.5, "change": 1, "cost": 0.3, "units": 40},
    {"name": "spare_van", "price": 0.1, "change": 300, "cost": 25, "units": 2},
    {"name": "late_permit", "price": 0.2, "change": 1, "cost": 0.4, "units": 60},
    {"name": "quota_waiver", "price": -0.05, "change": -200, "cost": 4, "units": 3},
]
for name, gain in worth_buying(offers):
    print(f"gain of {name}:", round(gain, 2))
print("offers kept:", len(worth_buying(offers)), "of", len(offers))
