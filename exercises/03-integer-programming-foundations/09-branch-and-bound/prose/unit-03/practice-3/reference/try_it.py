"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from strong import strong_choice

# Three candidates of a rota node whose LP value is 240.
trials = {"night_shift": (228.0, 239.5), "weekend_cover": (233.0, 234.0), "float_nurse": (None, 236.0)}
print("choice at parent 240:", strong_choice(240.0, trials))
print("choice without float_nurse:", strong_choice(240.0, {k: v for k, v in trials.items() if k != "float_nurse"}))
print("choice with equal drops:", strong_choice(50.0, {"p": (48.0, 47.0), "q": (47.0, 48.0)}))
