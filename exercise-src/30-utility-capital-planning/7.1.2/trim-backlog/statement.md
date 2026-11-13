A municipal utility (a fictional one) trims the trees along each of its circuits on a fixed
cycle: a circuit is **due** in year $`y`$ when at least `cycle` years have passed since it was last
trimmed ($`y - \text{last} \ge \text{cycle}`$). Its crews can trim at most `capacity` miles a year,
and a circuit is trimmed whole or not at all. Work that is due and not done stays due.

Write `plan_trims(circuits, cycle, capacity, years)` in `trims.py`. `circuits` maps a circuit id
to `(miles, year last trimmed)`. For each year of `years`, in order, the crews:

- take the circuits that are due, the one trimmed longest ago first (ties by circuit id);
- trim each one whose miles fit in what is left of the year's capacity, and pass over any that
  do not, going on down the list;
- record a trimmed circuit's new last-trim year, so its cycle restarts.

The result maps each year to a pair: the ids trimmed that year, sorted, and the **backlog**, the
miles that were due that year but not trimmed. The backlog counts every circuit due and left
untrimmed, whenever it first fell due: a circuit carried over from an earlier year counts again in
each year it is still waiting, and a circuit longer than `capacity`, which no year can trim, counts
in every year from the one it falls due.

Before you code, trace the instance with A (50 miles, last 2018), B (10, 2019), C (10, 2020), a
3-year cycle and 25 miles of capacity through 2024 by hand. The tests use small instances like it.
About fifteen lines.
