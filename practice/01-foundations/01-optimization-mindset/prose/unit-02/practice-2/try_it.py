"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pumps import Asset, Project, most_risk_removed, risk_avoided

wells = {
    "W1": Asset(age=35, cof=1000, beta=3.0, eta=40),
    "W2": Asset(age=20, cof=600, beta=2.5, eta=45),
    "W3": Asset(age=50, cof=300, beta=2.0, eta=60),
}
# A replacement and a repair for W1; G4 is ordered by the regulator.
work = [
    Project("G1", "W1", "replace", 400),
    Project("G2", "W1", "repair", 100),
    Project("G3", "W2", "replace", 350),
    Project("G4", "W3", "repair", 80, must_do=True),
]

for p in work:
    print(f"risk avoided by {p.pid} ({p.work} {p.asset}):", round(risk_avoided(p, wells), 2))
total, plan = most_risk_removed(work, wells, 500)
print("best plan at budget 500:", sorted(plan), round(total, 2))
