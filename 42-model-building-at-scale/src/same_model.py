"""Are two builders' models the same? Compare exported protos, then compare by name to find out why not.

`export_model()` gives the whole model as one protocol buffer, and two protos are equal only if every
id, name, bound, coefficient and the objective agree, in the same order. When they differ,
`differences` compares the models by name, which ignores the order of variables and rows and says
which ones disagree. GridCap is fictional.
"""

from __future__ import annotations

from dataclasses import replace

from ortools.math_opt.python import mathopt


def canonical(model: mathopt.Model) -> dict:
    """The model keyed by names: what it says, with the order things were added left out."""
    objective = model.objective
    return {
        "variables": {v.name: (v.lower_bound, v.upper_bound, v.integer) for v in model.variables()},
        "rows": {c.name: (c.lower_bound, c.upper_bound,
                          {t.variable.name: t.coefficient for t in c.terms()})
                 for c in model.linear_constraints()},
        "objective": (objective.is_maximize, objective.offset,
                      {t.variable.name: t.coefficient for t in objective.linear_terms()}),
    }


def differences(a: mathopt.Model, b: mathopt.Model, limit: int = 3) -> list[str]:
    """Up to `limit` readable differences between two models, compared by name."""
    ca, cb, out = canonical(a), canonical(b), []
    for kind in ("variables", "rows"):
        for name in sorted(ca[kind].keys() | cb[kind].keys()):
            left, right = ca[kind].get(name), cb[kind].get(name)
            if left != right:
                out.append(f"{kind[:-1]} {name}: {describe(left)} vs {describe(right)}")
    if ca["objective"] != cb["objective"]:
        out.append("objective differs")
    return out[:limit]


def describe(entry) -> str:
    if entry is None:
        return "missing"
    if len(entry) == 3 and isinstance(entry[2], dict):
        lb, ub, terms = entry
        shown = " + ".join(f"{c:g}*{v}" for v, c in sorted(terms.items())[:2])
        more = " + ..." if len(terms) > 2 else ""
        return f"[{lb:g}, {ub:g}] {len(terms)} terms" + (f": {shown}{more}" if terms else "")
    return str(entry)


if __name__ == "__main__":
    from gridcap import generate
    from loop_builder import build_loops
    from matrix_builder import build_matrix
    from tables import tables_of

    small = generate("small")
    tables = tables_of(small)
    loops = build_loops(small)

    matrix = build_matrix(tables)
    print("matrix builder:      protos equal:", loops.export_model() == matrix.export_model(),
          "| differences by name:", differences(loops, matrix))

    year_first = build_matrix(replace(tables, starts=tables.starts.sort_values(["start", "project_id"])))
    print("variables year-first: protos equal:", loops.export_model() == year_first.export_model(),
          "| differences by name:", differences(loops, year_first))

    late = build_matrix(replace(tables, costs=tables.costs.assign(k=tables.costs["k"] + 1)))
    print("costs one year late:  protos equal:", loops.export_model() == late.export_model())
    for line in differences(loops, late):
        print("  ", line)
