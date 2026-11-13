from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    starts: tuple[int, ...]


def add_works_rules(model: mathopt.Model, x: dict, projects: list[Project], blocks: list[list[str]],
                    platforms: dict[str, list[str]]) -> None:
    """Signal blocks done whole and in one year; each platform after one of its track upgrades."""
    starts = {p.pid: p.starts for p in projects}
    for block in blocks:
        lead = block[0]
        shared = set(starts[lead]).intersection(*(starts[m] for m in block[1:]))
        for member in block:
            for t in starts[member]:
                if t not in shared:
                    x[member, t].upper_bound = 0
        for member in block[1:]:
            for t in shared:
                model.add_linear_constraint(x[member, t] == x[lead, t], name=f"block_{member}_{t}")
    for platform, tracks in platforms.items():
        for t in starts[platform]:
            platform_by = sum(x[platform, u] for u in starts[platform] if u <= t)
            track_by = sum(x[k, u] for k in tracks for u in starts[k] if u <= t - 1)
            model.add_linear_constraint(platform_by <= track_by, name=f"carried_{platform}_{t}")


def build(projects: list[Project], blocks: list[list[str]],
          platforms: dict[str, list[str]]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="rail-works")
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    add_works_rules(model, x, projects, blocks, platforms)
    return model, x


if __name__ == "__main__":
    projects = [Project("SIG1", (2027, 2028)), Project("SIG2", (2028,)), Project("PLAT", (2029,)),
                Project("TRK", (2027, 2028))]
    model, x = build(projects, [["SIG1", "SIG2"]], {"PLAT": ["TRK"]})
    print(model.get_num_linear_constraints(), "rows")
