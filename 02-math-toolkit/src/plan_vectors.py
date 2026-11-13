"""A plan, the costs and the values as NumPy vectors: value and cost are dot products."""

import numpy as np

from gridcap import generate

tiny = generate("tiny")
ids = tiny.project_ids

capex = np.array([p.capex for p in tiny.projects])
npv = np.array([p.value for p in tiny.projects])


def to_vector(plan: set[str]) -> np.ndarray:
    return np.array([1 if pid in plan else 0 for pid in ids])


if __name__ == "__main__":
    x = to_vector({"P001", "P002", "P005", "P006"})
    print("x     =", x)
    print("capex =", capex)
    print("npv   =", npv)
    print("capex * x =", capex * x)
    print(f"capex @ x = {capex @ x:,}   npv @ x = {npv @ x:,}")
