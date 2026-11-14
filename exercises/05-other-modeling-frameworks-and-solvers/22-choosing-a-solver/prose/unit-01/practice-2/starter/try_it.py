"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from screen import screen

# What each solver refuses, and what it quietly changes.
table = {
    "Elm": {"refuses": {"sos2"}, "alters": set()},
    "Fir": {"refuses": set(), "alters": {"indicator", "general_integer"}},
    "Yew": {"refuses": {"quadratic", "indicator"}, "alters": set()},
}
print("model uses binary:", screen({"binary"}, table))
print("model uses indicator, general_integer:", screen({"indicator", "general_integer"}, table))
print("model uses sos2, quadratic:", screen({"sos2", "quadratic"}, table))
