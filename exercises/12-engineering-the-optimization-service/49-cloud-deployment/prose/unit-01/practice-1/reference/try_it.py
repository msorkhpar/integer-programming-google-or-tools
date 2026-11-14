"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from roster_settings import read_settings

full = {"ROSTER_BUCKET": "crews-demo", "SEASON": "2034", "CREWS": "7", "DRY_RUN": "False"}
print("full environment:", read_settings(full))
print("bucket and season only:", read_settings({"ROSTER_BUCKET": "crews-demo", "SEASON": "2029"}))
print("season soon, crews 80:", read_settings({"ROSTER_BUCKET": "crews-demo", "SEASON": "soon", "CREWS": "80"}))
print("with MAP_ACCESS_KEY set:", read_settings({**full, "MAP_ACCESS_KEY": "placeholder"}))
