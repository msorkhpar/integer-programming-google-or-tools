"""The same plan as a 0/1 vector: one decision variable per project."""

from gridcap import generate

tiny = generate("tiny")
ids = tiny.project_ids


def to_vector(plan: set[str]) -> list[int]:
    return [1 if pid in plan else 0 for pid in ids]


def objective(x: list[int]) -> int:
    return sum(p.value * xi for p, xi in zip(tiny.projects, x))


def spend(x: list[int]) -> int:
    return sum(p.capex * xi for p, xi in zip(tiny.projects, x))


if __name__ == "__main__":
    x = to_vector({"P001", "P002", "P006"})
    print("ids:", " ".join(ids))
    print("x:  ", "    ".join(str(v) for v in x))
    print(f"objective = {objective(x):,}, spend = {spend(x):,} <= {tiny.capital_budget:,}")
