This is the mock's whiteboard, coded. A port authority's planners override the optimizer, and one
built model must serve every what-if. `overrides.py` already has a start variable `x[(pid, year)]`
for each project and each year in its window, and the row that each project starts at most once.
Write `apply_overrides(model, x, projects, overrides)` for four kinds of override:

- `("start_in", pid, year)`: the project is funded and starts in that year;
- `("never", pid)`: the project is not funded;
- `("not_before", pid, year)`: if the project is funded, it starts in that year or later;
- `("fund", pid)`: the project is funded, in any year of its window.

Use variable bounds wherever one bound per variable can say the override, and a row only where it
cannot.

Check the overrides before any solve, and raise `ValueError` for two kinds that can never hold:

- a `start_in` year outside the project's window (there is no variable for it);
- overrides that contradict each other on one variable, leaving its lower bound above its upper
  bound (`start_in` and `never` on the same project, say). MathOpt refuses to solve a model with
  such a variable, so the clash is reported here, by name, instead. Write down, for each override, which bounds move or which labelled row is added before you
code it.

The tests fix plans and ask HiGHS whether the model allows them, so any correct formulation passes.
About twenty lines.
