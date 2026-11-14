"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from export import rejected, review

COLUMNS = ("id", "program", "region", "cost", "earliest", "latest", "must", "parent", "lag", "group", "crews")


def export(rows, budget="300"):
    return {"years": [2030, 2031], "rate": "0.04",
            "budgets": [{"year": str(y), "amount": budget} for y in (2030, 2031)],
            "projects": [dict(zip(COLUMNS, row)) for row in rows]}


good = [("K1", "lines", "South", "90;60", "2030", "2030", "1", "", "0", "", "1"),
        ("K2", "poles", "North", "70", "2030", "2031", "0", "K1", "1", "", "1")]
snap, findings = review(export(good))
print("two clean rows, budget 300:", findings, "accepted:", snap is not None)

messy = [("K1", "wires", "South", "9O", "2030", "2030", "1", "", "0", "", "1"),
         ("K2", "poles", "East", "70", "2031", "2030", "0", "K7", "1", "", "1")]
snap, findings = review(export(messy))
print("messy rows:", findings)

snap, findings = review(export(good, budget="50"))
print("two clean rows, budget 50:", findings, "rejected:", rejected(findings))
