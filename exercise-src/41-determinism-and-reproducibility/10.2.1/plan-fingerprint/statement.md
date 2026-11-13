A water utility replaces old mains. Its plan is a dict from a main's id to the year it is replaced,
for example `{"M07": 2028, "M12": 2027}`. The audit team stores one short id per plan, so that two
runs can be compared at a glance and an old plan can be found again by its id.

Write `fingerprint(plan)`. It returns 16 lowercase hex characters. Two plans with the same entries
get the same id, whatever order their dicts were built in and in whichever Python process the id
is computed. Plans whose entries differ in any way get different ids. Python's `hash()` is not an
option for this; the page says why.

About three lines.
