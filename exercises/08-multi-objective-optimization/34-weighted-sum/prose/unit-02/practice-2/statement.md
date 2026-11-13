A city parks department has a small budget and a short list of projects: new trees, a pond, play
courts and so on. Each costs money and adds two things the department reports on, square metres of
tree canopy (shade) and extra visits a week, both to maximize. The council has asked for "the best
plan at our weights", and the department suspects that the plan it would actually recommend is one
no weights would ever pick. It wants to find such a plan and show the council a proof it can check by
hand.

Write `unreachable(projects, budget)` in `parks.py`. A plan is any set of projects whose total cost
is within `budget`. Return a triple `(plan, a, b)` of sets of project names, or `None`:

- `plan` must be dominated by no allowed plan;
- `a` and `b` must be allowed plans with less and more shade than `plan`, and the straight line from
  `a` to `b` must pass strictly above `plan` (more visits at `plan`'s shade);
- return `None` only when every unbeaten plan is picked by some weighting.

An unbeaten plan that lies exactly on the straight line between two others counts as picked: at the
share where those two tie, it ties with them, so that weighting makes it optimal (it is supported,
lesson 8.1.2). Such a plan is never the answer, and when every unbeaten plan is a hull corner or on
a straight stretch between corners, the answer is `None`. The proof's line must pass *strictly*
above `plan`, as the second rule says.

The lists are short enough to try every set. Work it out on paper first: which points of the
shade-visits picture can a weighted sum return, and why does a line from `a` to `b` above `plan`
prove that no share picks `plan`? Then decide which two plans make a proof that always works.

About twenty-five lines.
