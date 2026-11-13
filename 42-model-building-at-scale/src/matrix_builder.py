"""The timing model built from DataFrames as whole columns: one table of (row, column, coefficient).

Every family of rows becomes a DataFrame of matrix entries, computed with merges and group
operations instead of Python loops. The arrays go into a MathOpt `ModelProto`, and
`Model.from_model_proto` turns that into the same model `build_loops` makes. GridCap is fictional.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from ortools.math_opt import model_pb2
from ortools.math_opt.python import mathopt

from tables import Tables

INF = float("inf")


def columns(t: Tables) -> pd.DataFrame:
    """One row per variable x[i, t], in the order the loop builder creates them; `col` is its id."""
    cols = t.starts[["project_id", "start", "npv"]].copy()
    cols["col"] = np.arange(len(cols))
    cols["name"] = "x_" + cols["project_id"] + "_" + cols["start"].astype(str)
    return cols


def entries(cols: pd.DataFrame, t: Tables) -> tuple[pd.DataFrame, pd.DataFrame]:
    """The rows (name, lb, ub) and the matrix entries (row, col, coef), family by family."""
    p = t.projects.reset_index(drop=True)

    # once_i / must_i: one row per project, a 1 for each of its start variables.
    once = pd.DataFrame({"name": np.where(p["must_do"], "must_", "once_") + p["project_id"],
                         "lb": np.where(p["must_do"], 1.0, -INF), "ub": 1.0, "key": p["project_id"]})
    once_terms = cols[["project_id", "col"]].rename(columns={"project_id": "key"}).assign(coef=1.0)

    # alt_g: one row per group, in the order groups first appear, a 1 for every member's start.
    groups = p.loc[p["alt_group"] != "", ["project_id", "alt_group"]]
    alt = pd.DataFrame({"key": groups["alt_group"].unique()})
    alt = alt.assign(name="alt_" + alt["key"], lb=-INF, ub=1.0)
    alt_terms = (groups.merge(cols[["project_id", "col"]], on="project_id")
                 .rename(columns={"alt_group": "key"})[["key", "col"]].assign(coef=1.0))

    # after_{c,t}: one row per child and child start t; +1 on the child's starts u <= t,
    # -1 on the parent's starts s <= t - lag.
    kids = p.loc[p["parent"] != "", ["project_id", "parent", "parent_lag"]]
    rows = kids.merge(cols[["project_id", "start"]], on="project_id")
    rows["key"] = rows["project_id"] + "@" + rows["start"].astype(str)
    after = rows.assign(name="after_" + rows["project_id"] + "_" + rows["start"].astype(str), lb=-INF, ub=0.0)
    mine = rows.merge(cols[["project_id", "start", "col"]], on="project_id", suffixes=("", "_u"))
    mine = mine[mine["start_u"] <= mine["start"]].assign(coef=1.0)
    theirs = rows.merge(cols[["project_id", "start", "col"]].rename(columns={"project_id": "parent"}),
                        on="parent", suffixes=("", "_s"))
    theirs = theirs[theirs["start_s"] <= theirs["start"] - theirs["parent_lag"]].assign(coef=-1.0)
    after_terms = pd.concat([mine, theirs])[["key", "col", "coef"]]

    # budget_y: one row per year; each start variable pays its cost profile, shifted to its start.
    budget = t.budget.assign(key=t.budget["year"].astype(str), name="budget_" + t.budget["year"].astype(str),
                             lb=-INF, ub=t.budget["budget"].astype(float))
    spend = cols[["project_id", "start", "col"]].merge(t.costs, on="project_id")
    spend["key"] = (spend["start"] + spend["k"]).astype(str)
    budget_terms = spend[["key", "col"]].assign(coef=spend["amount"].astype(float))

    families = [(once, once_terms), (alt, alt_terms), (after, after_terms), (budget, budget_terms)]
    row_tables, term_tables, offset = [], [], 0
    for rows_f, terms_f in families:
        rows_f = rows_f[["key", "name", "lb", "ub"]].reset_index(drop=True)
        rows_f["row"] = offset + np.arange(len(rows_f))
        offset += len(rows_f)
        row_tables.append(rows_f)
        term_tables.append(terms_f.merge(rows_f[["key", "row"]], on="key")[["row", "col", "coef"]])
    return pd.concat(row_tables, ignore_index=True), pd.concat(term_tables, ignore_index=True)


def build_matrix(t: Tables) -> mathopt.Model:
    cols = columns(t)
    rows, terms = entries(cols, t)
    terms = terms[terms["coef"] != 0].sort_values(["row", "col"], kind="stable")   # row-major, no zeros

    proto = model_pb2.ModelProto(name=f"{t.name} timing")
    proto.variables.ids.extend(cols["col"].tolist())
    proto.variables.lower_bounds.extend([0.0] * len(cols))
    proto.variables.upper_bounds.extend([1.0] * len(cols))
    proto.variables.integers.extend([True] * len(cols))
    proto.variables.names.extend(cols["name"].tolist())
    proto.linear_constraints.ids.extend(rows["row"].tolist())
    proto.linear_constraints.lower_bounds.extend(rows["lb"].tolist())
    proto.linear_constraints.upper_bounds.extend(rows["ub"].tolist())
    proto.linear_constraints.names.extend(rows["name"].tolist())
    proto.linear_constraint_matrix.row_ids.extend(terms["row"].tolist())
    proto.linear_constraint_matrix.column_ids.extend(terms["col"].tolist())
    proto.linear_constraint_matrix.coefficients.extend(terms["coef"].tolist())
    objective = cols[cols["npv"] != 0]
    proto.objective.maximize = True
    proto.objective.linear_coefficients.ids.extend(objective["col"].tolist())
    proto.objective.linear_coefficients.values.extend(objective["npv"].astype(float).tolist())
    return mathopt.Model.from_model_proto(proto)


if __name__ == "__main__":
    from gridcap import generate
    from loop_builder import solve_highs
    from tables import tables_of

    tables = tables_of(generate("small"))
    cols = columns(tables)
    rows, terms = entries(cols, tables)
    print(f"{len(cols)} columns, {len(rows)} rows, {len(terms)} entries; rows per family:",
          rows["name"].str.split("_").str[0].value_counts(sort=False).to_dict())
    child = tables.projects.loc[tables.projects["parent"] != ""].iloc[0]
    print(f"\n{child.project_id} follows {child.parent} with lag {child.parent_lag}; its rows' entries:")
    mine = rows[rows["name"].str.startswith(f"after_{child.project_id}_")]
    shown = (terms.merge(mine[["row", "name"]], on="row").merge(cols[["col", "name"]], on="col", suffixes=("", "_var"))
             .sort_values(["row", "col"])[["row", "name", "col", "name_var", "coef"]])
    print(shown.to_string(index=False))

    model = build_matrix(tables)
    result = solve_highs(model)
    x = {(r.project_id, r.start): model.get_variable(r.col) for r in cols.itertuples()}
    plan = sorted(key for key, var in x.items() if result.variable_values(var) > 0.5)
    print(f"\n{result.termination.reason.name}, NPV {result.objective_value():,.0f}k, {len(plan)} projects started;"
          f" first three: {plan[:3]}")
