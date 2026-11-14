"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from checks import precheck

money = {2030: 900, 2031: 1100}
crews = {2030: 15, 2031: 25}
minimum = {"cardiology": 500, "icu": 200}


def item(dept, cost, release, deadline, required, days, excludes=None):
    return {"dept": dept, "cost": cost, "release": release, "deadline": deadline, "required": required,
            "engineer_days": days, "excludes": excludes}


kit = {
    "ECHO-1": item("cardiology", 600, 2030, 2031, True, 12),
    "ECHO-2": item("cardiology", 400, 2031, 2031, False, 6, excludes="VENT-3"),
    "VENT-3": item("icu", 250, 2030, 2031, True, 4),
}
print("checks on the plain kit:", precheck(kit, money, crews, minimum))

kit["ECHO-1"]["engineer_days"] = 30
kit["ECHO-2"]["required"] = True
print("checks, ECHO-1 at 30 days, ECHO-2 required:", precheck(kit, money, crews, minimum))
print("checks, icu minimum 900:", precheck(kit, money, crews, {**minimum, "icu": 900}))
