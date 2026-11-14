"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from renovations import Renovation, forcing_cost

museum = [
    Renovation("gallery_roof", 30, 50),
    Renovation("cafe_fitout", 25, 30),
    Renovation("archive_hvac", 35, 45),
    Renovation("lobby_floor", 20, 18),
    Renovation("fire_doors", 10, 2, mandatory=True),
]
budget = 80

for name in ["lobby_floor", "gallery_roof", "fire_doors"]:
    print(f"reverse {name} at budget {budget}:", forcing_cost(museum, budget, name))
