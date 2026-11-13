"""Every rule of the tiny model as rows of A @ x <= b: flip >= rows, split == rows into two."""

import numpy as np

from budget_matrix import spend_matrix
from gridcap import generate

tiny = generate("tiny")
ids = list(tiny.project_ids)
n = len(ids)


def row(coeffs: dict[str, int]) -> np.ndarray:
    r = np.zeros(n, dtype=int)
    for pid, a in coeffs.items():
        r[ids.index(pid)] = a
    return r


def rule_rows() -> tuple[list[str], np.ndarray, np.ndarray]:
    names, rows, rhs = [], [], []

    def leq(name: str, coeffs: dict[str, int], limit: int) -> None:
        names.append(name)
        rows.append(row(coeffs))
        rhs.append(limit)

    for p in tiny.projects:
        if p.must_do:                                    # x = 1 is x <= 1 and -x <= -1
            leq(f"must_{p.project_id}_le", {p.project_id: 1}, 1)
            leq(f"must_{p.project_id}_ge", {p.project_id: -1}, -1)
        if p.parent:                                     # x_child <= x_parent
            leq(f"parent_{p.project_id}", {p.project_id: 1, p.parent: -1}, 0)
    leq("alt_G006", {"P006": 1, "P007": 1}, 1)           # at most one of the group
    return names, np.array(rows), np.array(rhs)


def full_model() -> tuple[list[str], np.ndarray, np.ndarray]:
    A_budget, b_budget = spend_matrix(tiny)
    names, A_rules, b_rules = rule_rows()
    budget_names = [f"budget_{y}" for y in tiny.years]
    return budget_names + names, np.vstack([A_budget, A_rules]), np.concatenate([b_budget, b_rules])


if __name__ == "__main__":
    names, A, b = full_model()
    print(f"{'row':12}", " ".join(f"{pid:>5}" for pid in ids), "|     b")
    for name, r, limit in zip(names, A, b):
        print(f"{name:12}", " ".join(f"{v:>5}" for v in r), f"| {limit:>5}")
    x = np.array([1, 0, 1, 1, 0, 0, 0, 0])
    broken = [name for name, ok in zip(names, A @ x <= b) if not ok]
    print("plan P001 P003 P004 breaks:", broken)
