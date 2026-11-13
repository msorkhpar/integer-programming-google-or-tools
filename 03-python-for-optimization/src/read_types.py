"""Read GridCap's projects.csv with pandas: the types it guesses, two ways they bite, and the fix."""

import io

import pandas as pd

from export import TYPES, tiny_export

with tiny_export() as folder:
    text = (folder / "projects.csv").read_text(encoding="utf-8")

print("projects.csv, first lines and a few columns:")
head = pd.read_csv(io.StringIO(text), nrows=4)
print(head[["project_id", "program", "cost_profile", "earliest_start", "must_do", "parent"]].to_string(index=False))

# 1. The type pandas guesses for a column depends on what is in it.
guessed = pd.read_csv(io.StringIO(text))
lines = text.splitlines()
vegetation = "\n".join([lines[0]] + [line for line in lines[1:] if ",vegetation," in line])
only_vegetation = pd.read_csv(io.StringIO(vegetation))
print()
print("cost_profile, all eight rows:     ", guessed["cost_profile"].dtype)
print("cost_profile, vegetation rows only:", only_vegetation["cost_profile"].dtype)
try:
    only_vegetation["cost_profile"].str.split(";")
except AttributeError as error:
    print("  .str.split fails:", error)

# 2. A blank cell is NaN, and NaN is true in an `if`.
print()
print("children counted with `if parent`:", sum(1 for parent in guessed["parent"] if parent))
print("children counted with .notna():   ", guessed["parent"].notna().sum())

# The fix: state the type of every column whose guess depends on its content (export.TYPES).
fixed = pd.read_csv(io.StringIO(vegetation), dtype=TYPES)
print()
print("vegetation rows only, read with dtype=TYPES:")
print("  cost_profile dtype:     ", fixed["cost_profile"].dtype)
print("  cost_profile split on ;:", fixed["cost_profile"].str.split(";").tolist())
print("  must_do:                ", fixed["must_do"].tolist())
print()

# A blank in an int64 column stops the read instead of turning the column into floats.
blank_start = text.replace(",2150,2028,", ",2150,,", 1)
print("blank earliest_start, guessed:", pd.read_csv(io.StringIO(blank_start))["earliest_start"].dtype)
try:
    pd.read_csv(io.StringIO(blank_start), dtype=TYPES)
except ValueError as error:
    print("blank earliest_start, dtype=TYPES:", error)
