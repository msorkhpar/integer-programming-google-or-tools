"""Lesson 4.5.1: the job shop moved onto GridCap's Valley circuits, in working days.

Each job passes through crews in its own order: a climbing crew cuts, a chipper crew clears the
brush, an inspector signs the circuit off. The corridor widening P006 starts with the chipper
crew's mower. Adapted from the OR-Tools job shop example,
https://developers.google.com/optimization/scheduling/job_shop. GridCap is fictional.
"""

from jobshop import jobshop

jobshop({"P003": [("climbers", 3), ("chipper", 2), ("inspector", 1)],
         "P010": [("climbers", 5), ("chipper", 3), ("inspector", 1)],
         "P018": [("climbers", 6), ("chipper", 4), ("inspector", 2)],
         "P006": [("chipper", 4), ("climbers", 3), ("inspector", 1)]})
