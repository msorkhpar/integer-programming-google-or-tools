"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from rescaling import ranking, survives_rescaling

reference = {"time": 5.0, "cost": 4.0}
projects = {"Quay": {"time": 4.0, "cost": 0.2}, "Mill": {"time": 0.3, "cost": 3.95},
            "Dock": {"time": 2.0, "cost": 2.0}}
to_minutes_and_k = {"time": 60.0, "cost": 0.001}


def weighted(benefit, ref):
    return 0.5 * benefit["time"] / ref["time"] + 0.5 * benefit["cost"] / ref["cost"]


def plain_sum(benefit, ref):
    return benefit["time"] + benefit["cost"]


print("ranking of 0.3, 0.9, 0.3:", ranking({"p": 0.3, "q": 0.9, "r": 0.3}))
print("weighted, minutes and $k:", survives_rescaling(weighted, projects, reference, to_minutes_and_k))
print("plain sum, minutes and $k:", survives_rescaling(plain_sum, projects, reference, to_minutes_and_k))
