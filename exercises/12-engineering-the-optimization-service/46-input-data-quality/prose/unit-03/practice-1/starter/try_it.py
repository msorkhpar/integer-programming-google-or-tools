"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from survey import digest

survey = {
    "version": 2, "survey": "Hillcrest", "rate": 0.25, "tags": ["steel", "urgent"],
    "segments": [{"id": "H2", "length_m": 64.0, "readings": [4.2, 4.1]},
                 {"id": "H1", "length_m": 30.5, "readings": [5.0, 4.95, 4.9]}],
}
shuffled = {**survey, "tags": ["urgent", "steel"], "segments": survey["segments"][::-1]}
rounded = {**survey, "rate": 0.2500001}
reading = {**survey, "segments": [{**survey["segments"][0], "readings": [4.1, 4.2]}, survey["segments"][1]]}

print("Hillcrest:            ", digest(survey)[:16])
print("tags and segments swapped:", digest(shuffled)[:16])
print("rate 0.2500001:       ", digest(rounded)[:16])
print("H2 readings reversed: ", digest(reading)[:16])
try:
    digest({**survey, "rate": float("nan")})
except ValueError as e:
    print("rate nan raised:", e)
