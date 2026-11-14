"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from hospital_audit import audit_failures

items = {
    "pet_scan": {"years": [2031, 2032], "cost": 2000, "mandatory": False},
    "ultrasound": {"years": [2030, 2031], "cost": 600, "mandatory": False},
    "autoclave": {"years": [2030], "cost": 300, "mandatory": True},
    "monitors": {"years": [2030, 2031, 2032], "cost": 500, "mandatory": False},
}
budget = {2030: 1000, 2031: 2200, 2032: 1500}
groups = {"scanners": ["pet_scan", "ultrasound"]}

print("autoclave 2030, monitors 2031:", audit_failures({"autoclave": 2030, "monitors": 2031}, items, budget, groups))
print("pet_scan 2030, monitors 2030:", audit_failures({"pet_scan": 2030, "monitors": 2030}, items, budget, groups))
print("autoclave 2030, pet_scan + ultrasound + monitors 2031:",
      audit_failures({"autoclave": 2030, "pet_scan": 2031, "ultrasound": 2031, "monitors": 2031},
                     items, budget, groups))
