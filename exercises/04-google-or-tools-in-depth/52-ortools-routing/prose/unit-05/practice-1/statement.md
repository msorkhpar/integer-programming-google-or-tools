A laundry's dispatch report is checked by two people every morning, and they must get the same
routes from the same data. The routing code is fine; the search settings are not. Write
`search_parameters(strategy, metaheuristic=None, solutions=None)` in `search.py`. It turns names
such as `"SAVINGS"` and `"GUIDED_LOCAL_SEARCH"` into OR-Tools search parameters, and enforces the
team's rule for repeatable runs:

- the run never stops on wall time, so the parameters carry **no time limit**;
- a metaheuristic that leaves local minima on purpose (anything but `GREEDY_DESCENT`) **always has
  a solution limit**: `solutions` if given, otherwise `DEFAULT_SOLUTIONS` (200);
- `GREEDY_DESCENT` and the default search stop at their local minimum by themselves, so they get a
  solution limit only when `solutions` is given.

There is no model to formulate here: the routing model is fixed, and the choice is how to search
it. Before you code, write the rule above as a small decision table (metaheuristic named or not,
`solutions` given or not, the resulting `solution_limit`), and say which enum class each name
belongs to in `routing_enums_pb2`.

The tests read the parameters and run one small model twice. About eight lines.
