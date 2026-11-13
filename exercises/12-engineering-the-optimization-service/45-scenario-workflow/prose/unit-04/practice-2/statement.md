The school district (invented for this practice) keeps its yearly budget plans in a `budget_plan`
table (see `SCHEMA` in `guards.py`). Several scripts and a reporting tool write to that table
directly, so these rules must be kept by the database itself, whoever writes:

- A fiscal year has at most one plan with status `approved`. Any number of drafts may exist
  for the same year.
- An approved plan can never be changed, while a draft can be edited and approved.
- An approved plan can never be deleted; a draft can.

Write the SQL statements in `GUARDS` that keep these rules. `open_db` runs `SCHEMA` and then
`GUARDS`. A refused change must raise `sqlite3.IntegrityError`. Three statements.
