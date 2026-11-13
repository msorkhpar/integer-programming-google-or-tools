from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_sequence_rules(model: mathopt.Model, patch: dict, replace: dict,
                       roofs: dict[str, tuple[tuple[int, ...], tuple[int, ...]]], gap: int, warranty: int) -> None:
    """A replacement at least `gap` years after a patch; no patch within the new roof's warranty."""
    # TODO: one row per roof and replacement year.
    return None


def build(roofs: dict[str, tuple[tuple[int, ...], tuple[int, ...]]], gap: int,
          warranty: int) -> tuple[mathopt.Model, dict, dict]:
    model = mathopt.Model(name="roofs")
    patch = {(r, s): model.add_binary_variable(name=f"patch_{r}_{s}") for r, (ps, _) in roofs.items() for s in ps}
    replace = {(r, t): model.add_binary_variable(name=f"replace_{r}_{t}") for r, (_, ts) in roofs.items() for t in ts}
    for r, (ps, ts) in roofs.items():
        model.add_linear_constraint(sum(patch[r, s] for s in ps) <= 1, name=f"once_patch_{r}")
        model.add_linear_constraint(sum(replace[r, t] for t in ts) <= 1, name=f"once_replace_{r}")
    add_sequence_rules(model, patch, replace, roofs, gap, warranty)
    return model, patch, replace


if __name__ == "__main__":
    model, patch, replace = build({"LIB": ((2027, 2028), (2029, 2030))}, gap=2, warranty=3)
    print(model.get_num_linear_constraints(), "rows")
