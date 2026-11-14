"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from generators import bounds, tight_m

# Sites: value per generator-hour, hours usable, hookup fee. Fleet of 60 hours.
sites = {"North": (30, 40, 200), "Pier": (20, 90, 150), "Depot": (35, 25, 600)}

print("tight M at fleet 60:", tight_m(sites, 60))
for name, value in bounds(sites, 60).items():
    print(f"{name} bound at fleet 60:", round(value, 2))
