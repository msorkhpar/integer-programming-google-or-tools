from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Vessel:
    vid: str
    years: tuple[int, ...]


def apply_overrides(x: dict, vessels: list[Vessel], overrides: list[tuple]) -> list:
    """Lock, ban and deadline overrides as bounds on x; return what undoes them."""
    years = {v.vid: v.years for v in vessels}
    changes = []
    for kind, vid, *rest in overrides:
        for t in years[vid]:
            low, high = x[vid, t].lower_bound, x[vid, t].upper_bound
            changes.append((x[vid, t], low, high))
            closed = kind == "ban" or (kind == "lock" and t != rest[0]) or (kind == "by" and t > rest[0])
            high = 0 if closed else high
            low = 1 if kind == "lock" and t == rest[0] else low
            x[vid, t].lower_bound, x[vid, t].upper_bound = low, high
    return changes


def undo_overrides(changes: list) -> None:
    """Put back every bound that `apply_overrides` changed."""
    for var, low, high in reversed(changes):
        (var.lower_bound, var.upper_bound) = (low, high)


def build(vessels: list[Vessel]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="dry-docks")
    x = {(v.vid, t): model.add_binary_variable(name=f"x_{v.vid}_{t}") for v in vessels for t in v.years}
    for v in vessels:
        model.add_linear_constraint(sum(x[v.vid, t] for t in v.years) <= 1, name=f"once_{v.vid}")
    return model, x


if __name__ == "__main__":
    vessels = [Vessel("ISLA", (2027, 2028, 2029))]
    model, x = build(vessels)
    changes = apply_overrides(x, vessels, [("by", "ISLA", 2028)])
    print(x["ISLA", 2029].upper_bound)
    undo_overrides(changes)
    print(x["ISLA", 2029].upper_bound)
