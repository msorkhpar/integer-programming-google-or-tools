"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from review import Job, conflicts

# A tram depot's jobs: start years, crew, optional predecessor and lag.
jobs = {
    "WHEELS": Job((2027, 2028), "red"),
    "BRAKES": Job((2027, 2028, 2029), "red"),
    "SEATS": Job((2028, 2029), "blue"),
    "LIGHTS": Job((2029, 2030, 2031), "green", follows="SEATS", lag=1),
}

print("WHEELS 2027, SEATS 2028, LIGHTS 2029:",
      conflicts(jobs, [("lock", "WHEELS", 2027), ("lock", "SEATS", 2028), ("lock", "LIGHTS", 2029)]))
print("SEATS 2027:", conflicts(jobs, [("lock", "SEATS", 2027)]))
print("WHEELS 2028, BRAKES 2028:", conflicts(jobs, [("lock", "WHEELS", 2028), ("lock", "BRAKES", 2028)]))
print("BRAKES 2029 and ban BRAKES:", conflicts(jobs, [("lock", "BRAKES", 2029), ("ban", "BRAKES")]))
print("SEATS 2029, LIGHTS 2029:", conflicts(jobs, [("lock", "SEATS", 2029), ("lock", "LIGHTS", 2029)]))
