"""Lesson 14.1.7: the tests the lesson adds, run against the project before it (steps/06) and after it
(steps/07), what the step did to the size of the code, and the golden record of the small season."""

from snapshots import print_before_after, print_sizes, step_dir

print_before_after(7)
print()
print_sizes(6, 7)
print()
print((step_dir(7) / "tests" / "golden" / "small.json").read_text(), end="")
