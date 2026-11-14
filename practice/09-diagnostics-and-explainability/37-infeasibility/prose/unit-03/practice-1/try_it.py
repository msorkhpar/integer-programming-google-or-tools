"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from timetable import conflict_among

soft = ["9C_afternoons", "9C_gym_wed", "gym_shut_wed", "10D_gym_wed"]
hard = ["one_class_per_room", "teacher_max_5"]


def oracle(*clashes):
    sets = [set(c) for c in clashes]
    return lambda on: any(c <= set(on) for c in sets)


print("conflict, gym shut on Wednesday:", conflict_among(soft, hard, oracle(["9C_gym_wed", "gym_shut_wed"])))
print("conflict, two classes in the gym:",
      conflict_among(soft, hard, oracle(["9C_gym_wed", "10D_gym_wed", "one_class_per_room"])))
print("conflict, nothing clashes:", conflict_among(soft, hard, oracle(["no_such_rule"])))
