"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from roof_backtest import summarize

archive = [
    {"cycle": 2019, "approved": {"annex": 2020, "library": 2021, "canteen": 2021, "studio": 2022}},
    {"cycle": 2020, "approved": {"library": 2021}},
    {"cycle": 2021, "approved": {}},
]
rerun = {
    2019: {"annex": 2020, "library": 2022, "theatre": 2021},
    2021: {"canteen": 2023},
}
rows = summarize(archive, rerun)
print("rows for 3 archived cycles:", len(rows))
for row in rows:
    print(f"cycle {row['cycle']}:", row)
