"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from relaxation import relaxation_changes

# Variable values read from a model after feasRelax.
values = {"shift_4": 1.0, "ArtP_cover_dock": 2.0, "ArtN_hours_ana": 3.5, "ArtNB_hours_ana": 1.0,
          "ArtU_overtime": 6.0, "ArtL_trainees": 0.0}
print("changes:", relaxation_changes(values))
print("changes at tolerance 3:", relaxation_changes(values, tol=3.0))
