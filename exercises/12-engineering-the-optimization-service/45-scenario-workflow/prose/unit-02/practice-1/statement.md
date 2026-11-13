Riverbend Water (invented for this practice) lets its engineers narrow when a main replacement may
start. Each project has a start window, a `range` of years, and one start variable $`x_t \in \{0,1\}`$
per year $`t`$ of the window, with bounds $`l_t \le x_t \le u_t`$. Three kinds of override exist:

- `start_in`, with `years = (y,)`: the project starts in year $`y`$.
- `only_between`, with `years = (a, b)`: the project may start only from $`a`$ to $`b`$, both
  included; it does not have to start at all.
- `skip_years`, with any number of years: the project may not start in those years (a road is
  closed, a festival needs the street); it does not have to start at all.

Write `bounds_for(kind, years, window)` in `overrides.py`. It returns `{t: (l_t, u_t)}` for every
year `t` of the window, with `(0, 1)` for a year the override leaves free. An override that would
set every year of the window to `(0, 0)` would quietly take the project out of the plan, which is
not what was asked: return `None` for it instead, so the service can refuse it. A `start_in` year
outside the window falls under that rule too. A `kind` that is none of the three narrows nothing:
every year of the window gets `(0, 1)`. About twelve lines.
