A water utility's planners keep asking two questions about their project list before any model is
solved. Each project has a cost (in $k) and a tuple of `needs`: the projects that must also be
funded for it to go ahead. A needed project may have needs of its own, and two projects may need
the same one.

- "What does it take to fund this project?" `entry_cost(projects, pid)` returns the cost of `pid`
  plus the cost of every project it needs, directly or through other needed projects. A project
  that is needed along two paths is still built, and paid for, once.
- "Which projects are required only because something required needs them?"
  `implied_required(projects, required)` returns the set of projects that are not in `required`
  but that some project in `required` needs, directly or indirectly.

`projects` maps each id to a `Project`. No project needs itself, directly or indirectly.

Write both functions in `entry.py`. Draw the needs of the test instances as a graph first (an arrow
from each project to each project it needs), and decide what a walk over that graph must remember.
About fifteen lines.
