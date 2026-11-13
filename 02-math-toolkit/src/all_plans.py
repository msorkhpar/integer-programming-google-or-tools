"""All 256 plans of the tiny portfolio as the columns of one matrix, checked by one product."""

import itertools

import numpy as np

from gridcap import generate
from rules_matrix import full_model

tiny = generate("tiny")
ids = tiny.project_ids
npv = np.array([p.value for p in tiny.projects])
names, A, b = full_model()

X = np.array(list(itertools.product([0, 1], repeat=len(ids)))).T     # 8 rows, 256 columns
activity = A @ X                                                      # 7 rows, 256 columns
feasible = np.all(activity <= b[:, None], axis=0)                     # one True/False per plan
values = np.where(feasible, npv @ X, -1)
best = X[:, np.argmax(values)]

if __name__ == "__main__":
    print("X:", X.shape, " A @ X:", activity.shape)
    print("feasible plans:", int(feasible.sum()), "of", X.shape[1])
    print("best:", [pid for pid, xi in zip(ids, best) if xi], f"value ${npv @ best:,}k")
    print("spend by year:", dict(zip(tiny.years, (A @ best)[:3].tolist())))
