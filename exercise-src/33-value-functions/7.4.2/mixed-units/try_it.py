"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from stops import rank, score

reference = {"time": (400, "hours"), "complaints": (5, "dozen complaints"), "savings": (150, "$k")}
weights = {"time": 0.4, "complaints": 0.3, "savings": 0.3}
stops = {
    "Pine": {"time": (6_000, "minutes"), "complaints": (12, "complaints"), "savings": (30_000, "$")},
    "Maple": {"time": (40, "hours"), "complaints": (3, "dozen complaints"), "savings": (75, "$k")},
    "Spruce": {"time": (200, "hours"), "complaints": (0, "complaints"), "savings": (0, "$k")},
}

for name, b in stops.items():
    print(f"{name} score:", round(score(b, reference, weights), 4))
print("ranked:", rank(stops, reference, weights))
