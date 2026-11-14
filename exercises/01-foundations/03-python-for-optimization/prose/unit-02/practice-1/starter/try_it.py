"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from assets import parse_assets

rows = [
    {"asset_id": "T-07", "kind": "transformer", "region": "North", "age": "22", "weibull_beta": "2.8",
     "weibull_eta": "48", "rul": "15", "cof": "2400"},
    {"asset_id": "T-08", "kind": "transformer", "region": "Central", "age": "5", "weibull_beta": "2.8",
     "weibull_eta": "48", "rul": "30", "cof": "2400"},
    {"asset_id": "S-31", "kind": "switch", "region": "South", "age": "17", "weibull_beta": "1.9",
     "weibull_eta": "", "rul": "8", "cof": "150"},
]
assets, rejected = parse_assets(rows)
for a in assets:
    print("valid row:", a.asset_id, "age", a.age, "eta", a.weibull_eta)
print("rejected (row, field):", rejected)
