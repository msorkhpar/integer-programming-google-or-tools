"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from raises import smallest_raise

cost = {"S1": 500, "S2": 400, "S3": 250}

print("raise, S1 and S2 fixed to 2030:", smallest_raise({"S1": [2030], "S2": [2030]}, cost, {2030: 700, 2031: 0}))
print("raise, S1 may move to 2031:",
      smallest_raise({"S1": [2030, 2031], "S2": [2030]}, cost, {2030: 700, 2031: 450}))
print("raise, three jobs over two years:",
      smallest_raise({"S1": [2030], "S2": [2031], "S3": [2031]}, cost, {2030: 300, 2031: 600}))
