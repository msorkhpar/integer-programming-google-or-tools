"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from npv import npv_table

# Two invented projects, money in $k.
snapshot = {
    "years": [2031, 2032, 2033], "rate": 0.06,
    "projects": {
        "M1": {"cost": [120], "earliest": 2031, "latest": 2033},
        "M2": {"cost": [60, 60], "earliest": 2031, "latest": 2032},
    },
}
forecast = {"M1": {"benefits": [50, 50, 50], "decay": 0.0},
            "M2": {"benefits": [45, 45, 45, 45], "decay": 0.08}}

table = npv_table(snapshot, forecast)
print("starts in the table:", len(table))
for (pid, start), value in table.items():
    print(f"NPV of {pid} started {start}:", value)
