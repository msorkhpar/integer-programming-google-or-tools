"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from trails import Trail, most_visitors

reserve = [Trail("Falls Path", 1_100, 8, 35), Trail("Bog Walk", 350, 70, 30),
           Trail("Pine Ridge", 650, 30, 25), Trail("Creek Loop", 450, 15, 20)]

for floor in (0, 40, 90, 140):
    print(f"budget 80, at least {floor} acres:", most_visitors(reserve, 80, floor))
