"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from best_plans import all_best

# Workshop talks: score, minutes, track.
talks = {"W1": (3, 20, "ml"), "W2": (2, 10, "ml"), "W3": (3, 20, "db"), "W4": (1, 10, "db"), "W5": (2, 10, "ui")}


def session(minutes):
    model = cp_model.CpModel()
    x = {t: model.new_bool_var(t) for t in talks}
    model.add(sum(m * x[t] for t, (_, m, _) in talks.items()) <= minutes)
    for track in {k for _, _, k in talks.values()}:
        model.add_at_most_one(x[t] for t, (_, _, k) in talks.items() if k == track)
    return model, x, sum(s * x[t] for t, (s, _, _) in talks.items())


for minutes in (30, 40, 50):
    best, plans = all_best(*session(minutes))
    print(f"best score in {minutes} minutes:", best)
    print(f"  plans in {minutes} minutes:", plans)
