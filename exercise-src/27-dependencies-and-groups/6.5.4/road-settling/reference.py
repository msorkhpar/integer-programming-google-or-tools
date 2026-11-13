from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]
    duration: int = 1


def add_after_rules(model: mathopt.Model, x: dict, projects: list[Project],
                    after: dict[str, tuple[str, int]]) -> None:
    """Each resurfacing starts only once its water main is finished and the trench has settled."""
    by_id = {p.pid: p for p in projects}
    for street, (main, settle) in after.items():
        gap = by_id[main].duration + settle
        for t in by_id[street].starts:
            paved_by = sum(x[street, u] for u in by_id[street].starts if u <= t)
            ready_by = sum(x[main, s] for s in by_id[main].starts if s + gap <= t)
            model.add_linear_constraint(paved_by <= ready_by, name=f"settled_{street}_{t}")


def build(projects: list[Project], after: dict[str, tuple[str, int]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="streets")
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    add_after_rules(model, x, projects, after)
    return model, x


if __name__ == "__main__":
    projects = [Project("MAIN", (2027, 2028), 2), Project("PAVE", (2029, 2030, 2031))]
    model, x = build(projects, {"PAVE": ("MAIN", 1)})
    print(model.get_num_linear_constraints(), "rows")
