"""Find where the slow builder spends its time with cProfile, on the first 2,500 projects of large.

cProfile counts every call of every function and times them. The counts depend only on the data
and the code, so they repeat exactly; the times do not, so they are printed apart. GridCap is
fictional.
"""

from __future__ import annotations

import cProfile
import pstats

from gridcap import generate
from growth import first_rows
from slow_builder import build_slow
from tables import tables_of

WATCH = {                                       # (file ending, function) -> what the line means
    ("slow_builder.py", "build_slow"): "the whole build",
    ("frame.py", "iterrows"): "DataFrame.iterrows, one Series per row",
    ("generic.py", "__getattr__"): "row.column, reading a field by name",
    ("slow_builder.py", "starts_of"): "starts_of, a mask over every start row",
    ("series.py", "_cmp_method"): "column == value, computing each mask",
    ("frame.py", "_getitem_bool_array"): "df[mask], selecting each mask's rows",
    ("model.py", "add_linear_constraint"): "Model.add_linear_constraint",
    ("model.py", "add_variable"): "Model.add_variable",
}

if __name__ == "__main__":
    tables = first_rows(tables_of(generate("large")), 2_500)
    profiler = cProfile.Profile()
    profiler.enable()
    build_slow(tables)
    profiler.disable()
    stats = pstats.Stats(profiler).stats        # (file, line, function) -> (calls, ..., cumulative time, ...)

    rows = []                                   # in WATCH's order, so the table's shape never moves
    for (ending, name), meaning in WATCH.items():
        for (file, _, function), (_, calls, _, cumulative, _) in stats.items():
            if file.endswith(ending) and function == name:
                rows.append((meaning, calls, cumulative))
    whole = rows[0][2]
    print(f"{'function':42} {'calls':>8}")
    for meaning, calls, _ in rows:
        print(f"{meaning:42} {calls:>8,}")
    print()
    print("measured (cumulative time, and its share of the whole build):")
    for meaning, _, cumulative in rows:
        print(f"{meaning:42} {cumulative:7.3f}s {cumulative / whole:5.0%}")
