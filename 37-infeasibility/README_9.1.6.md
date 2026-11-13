# 9.1.6 Turning an IIS Into a Planner Message

GridCap's planners do not read `after_P023_2029`. They read "P023 needs P022 started a year
before it". The Budget Lock scenario now has everything a diagnosis can give it: a pre-solve check
that fired (lesson 9.1.2), three conflicts (lessons 9.1.3 and 9.1.5) and a priced repair
(lesson 9.1.4). None of it is yet something a planner, a finance lead or the board can act on.
This lesson turns a conflict into a message: the rules in plain words, the arithmetic that shows
why they clash, and the changes that would end it. It ends with section 9's milestone, the whole
Budget Lock scenario explained in one message. GridCap is a fictional utility; none of its numbers
are real.

## The Model

The model of lesson 9.1.1, unchanged, with its formulation and row labels there. This lesson reads
row names, never rows, so here is the vocabulary it translates, with the data each kind of row
carries:

| Row name | Rule | Data the message needs |
| --- | --- | --- |
| `must_P017` | $`\sum_{t \in T_i} x_{i,t} = 1`$ | the project's name and window $`T_i`$ |
| `force_P023`, `force_P032_2028` | $`\sum_t x_{i,t} \ge 1`$, $`x_{i,f_i} \ge 1`$ | the project, the forced year |
| `after_P023_2029` | $`\sum_{u \le t} x_{c,u} \le \sum_{s \le t - L_c} x_{p(c),s}`$ | child, parent, lag $`L_c`$ |
| `budget_2028` | $`\text{spend}_y \le B_y`$ | $`B_y`$, and GridCap's own figure if the scenario changed it |
| `crews_transmission_2030` | crew-months used $`\le K_{q,y}`$ | $`K_{q,y}`$, and GridCap's own figure |
| `floor_Coast`, `alt_G001`, `once_P001`, `drop_P040` | as in lesson 9.1.1 | the region's floor; the group's members; the project |

A row name is built from a kind and its indices (`budget` and `2028`), so the translator splits the
name and looks the indices up in the portfolio and the scenario.

## A Planner Message Names Rules and Projects, Never Rows

`message.describe(name, portfolio, scenario)` turns one row name into one sentence. Each kind of
row gets its own wording, with the project's id *and* name, money in $k, and a note when a number
is the scenario's rather than GridCap's own:

```python
    if kind == "after":
        pid, year = rest.rsplit("_", 1)
        c = portfolio.project(pid)
        return (f"{label(portfolio, pid)} may start in {year} only if {label(portfolio, c.parent)} "
                f"has started by {int(year) - c.parent_lag}.")
    if kind == "budget":
        year = int(rest)
        if year in scenario.budget:
            return f"Finance locked the {year} budget at ${scenario.budget[year]:,}k (GridCap's figure: ${portfolio.budget[year]:,}k)."
        return f"The {year} budget is ${portfolio.budget[year]:,}k."
```

Three choices make the difference between a translation and a message:

- **Say who set the number.** "Finance locked the 2028 budget at $6,000k (GridCap's figure:
  $8,120k)" tells the reader that the number is a decision someone made, and whom to ask.
- **State a precedence row as the condition it is.** The row `after_P023_2029` holds for every
  plan that does not start P023 in 2029. What it forbids is P023 in 2029 without P022 by 2028, so
  that is what the sentence says.
- **Name the project twice.** The id (`P023`) is what planners search for. The name (`Valley pole
  run replace (A023)`) is what they recognize.

<!-- practice 1 -->

## Show the Arithmetic: Every Way to Start the Projects, and Where It Runs Out

A list of rules says *that* they clash. A planner who does not trust the model wants to see *why*.
For the small conflicts an IIS gives, the "why" can be worked out completely. List the projects
the conflict requires, and the start years its rows leave each one. Then try every combination,
and for each, find the budget or crew row it overruns:

```python
    for choice in product(*(years[p] for p in pids)):
        for row in rows:
            parts = {p: use(portfolio, row, p, t) for p, t in zip(pids, choice) if use(portfolio, row, p, t)}
            need, have = sum(parts.values()), capacity(portfolio, scenario, row)
            if need > have:
```

`starts` builds the year lists from the rows. A must-do project gets its window. A forced project
gets its window, or only the forced year. And a parent gets the years its child's precedence row
allows: when the conflict pins P023 to 2029, its parent P022 may start only in 2027 or 2028. On
the override conflict with the 2028 budget, that gives two combinations:

```text
Why:
  - Starting P022 in 2027, P023 in 2029, P032 in 2028: the 2028 budget must cover $6,400k (P022 $720k + P032 $5,680k) but has $6,000k.
  - Starting P022 in 2028, P023 in 2029, P032 in 2028: the 2028 budget must cover $6,040k (P022 $360k + P032 $5,680k) but has $6,000k.
```

Every combination fails, which is the conflict, shown in sums a planner can check by hand. The
cheapest combination misses by $40k, and that is exactly the 2028 budget increase in the priced
repair of lesson 9.1.4. The arithmetic and the elastic model agree.

The enumeration is safe here because an IIS is small: three projects with at most two start years
each. On a conflict with many projects it would grow quickly, and the message should then show
only the combination that comes closest.

<!-- practice 2 -->

## Each Conflict Ends With the Changes That End It, in the Planners' Words

An IIS has a property that makes the last line of a message easy to write. Remove any one of its
rules and the rest can hold. So every rule in the conflict that a person can change is a way out
of *that* conflict. `remedy` says each way out in words, and returns nothing for the model's own
rules (precedence, "at most once", alternatives), which no meeting can change:

```python
    if kind == "budget":
        return f"raise the {rest} budget"
    if kind == "crews":
        program, year = rest.rsplit("_", 1)
        return f"find more {program} crew-months for {year}"
```

```text
Any one of these changes ends this conflict: stop forcing P023 into the plan; let P032 start in another year; raise the 2028 budget.
```

The sentence says "this conflict" on purpose. Ending one conflict need not give a plan. Lesson
9.1.3's loop showed that the override conflict with the 2028 crews hides a second one with the
2028 budget. A message that offered "raise the 2028 budget" as *the* fix would be wrong. So a
message lists every conflict, and then one repair for the whole scenario, checked by a solve.

## One Message for the Whole Scenario

`lock_message.py` puts the module together. It runs the pre-solve checks (lesson 9.1.2), finds
every conflict with the deletion-filter loop (lesson 9.1.3), explains each one with this lesson's
functions, and then takes the priced repair of lesson 9.1.4. It writes the repair as a new scenario
and solves it, so that the message never promises a plan the model has not found:

```python
repaired = replace(scenario, name="repaired", budget=budget, crews=crews)
result = solve(build(small, repaired).model)
```

The whole message, as a planner receives it:

```text
Scenario 'budget-lock' has no plan that keeps every rule.
Found before solving: P017: needs 13 transmission crew-months a year; [12, 12] in [2030, 2031].

Conflict 1 of 3. These rules cannot all hold:
  - Planners forced P023 Valley pole run replace (A023) into the plan.
  - Planners forced P032 Valley tower set repair (A032) into the plan, starting in 2028.
  - P023 Valley pole run replace (A023) may start in 2029 only if P022 Valley tower set repair (A022) has started by 2028.
  - Transmission crews have 19 crew-months in 2028.
Why:
  - Starting P022 in 2027, P023 in 2029, P032 in 2028: transmission crews in 2028 must cover 20 crew-months (P022 6 crew-months + P032 14 crew-months) but have 19 crew-months.
  - Starting P022 in 2028, P023 in 2029, P032 in 2028: transmission crews in 2028 must cover 20 crew-months (P022 6 crew-months + P032 14 crew-months) but have 19 crew-months.
Any one of these changes ends this conflict: stop forcing P023 into the plan; let P032 start in another year; find more transmission crew-months for 2028.

Conflict 2 of 3. These rules cannot all hold:
  - Planners forced P023 Valley pole run replace (A023) into the plan.
  - Planners forced P032 Valley tower set repair (A032) into the plan, starting in 2028.
  - P023 Valley pole run replace (A023) may start in 2029 only if P022 Valley tower set repair (A022) has started by 2028.
  - Finance locked the 2028 budget at $6,000k (GridCap's figure: $8,120k).
Why:
  - Starting P022 in 2027, P023 in 2029, P032 in 2028: the 2028 budget must cover $6,400k (P022 $720k + P032 $5,680k) but has $6,000k.
  - Starting P022 in 2028, P023 in 2029, P032 in 2028: the 2028 budget must cover $6,040k (P022 $360k + P032 $5,680k) but has $6,000k.
Any one of these changes ends this conflict: stop forcing P023 into the plan; let P032 start in another year; raise the 2028 budget.

Conflict 3 of 3. These rules cannot all hold:
  - P017 Coast tower set repair (A017) is must-do: it has to start in 2030 or 2031.
  - Transmission crews have 12 crew-months in 2030 in this scenario (GridCap's figure: 34).
  - Transmission crews have 12 crew-months in 2031 in this scenario (GridCap's figure: 14).
Why:
  - Starting P017 in 2030: transmission crews in 2030 must cover 13 crew-months (P017 13 crew-months) but have 12 crew-months.
  - Starting P017 in 2031: transmission crews in 2031 must cover 13 crew-months (P017 13 crew-months) but have 12 crew-months.
Any one of these changes ends this conflict: find more transmission crew-months for 2030; find more transmission crew-months for 2031.

The cheapest repair, with a crew-month priced at $50k and a broken must-do or override at $10,000k:
  - the 2028 budget: $6,040k instead of $6,000k
  - distribution crews in 2030: 13 crew-months instead of 8
  - transmission crews in 2028: 20 crew-months instead of 19
  - transmission crews in 2031: 13 crew-months instead of 12
With these, the model finds a plan: OPTIMAL, NPV $17,060k.
```

Read it as the board would. Conflicts 1 and 2 share the board's two overrides, so one decision
(stop forcing P023, or let P032 start another year) ends both. Conflict 3 is the crew cut and was
found before any solve. If the board keeps its overrides, the cheapest way to a plan is $40k and
seven crew-months, and that plan is worth $17,060k. No row name appears anywhere in the message.
Every number in it can be checked against the data, and the repair has been checked by a solve.

## Summary

- **A planner message names rules and projects, never rows.** Say who set each number, state a
  precedence row as the condition it forbids, and name each project by id and by name.
- **Show the arithmetic.** For an IIS's few projects, try every start-year combination and show
  where each one runs out. The closest miss, $40k, matched the elastic repair.
- **Each conflict ends with the changes that end it, in the planners' words.** Any one changeable
  rule of an IIS ends that conflict, and not necessarily the scenario's infeasibility.
- **One message for the whole scenario:** the check, every conflict, and one repair checked by a
  solve. That is section 9's milestone.

## Reference

| Part of the message | Comes from | Lesson |
| --- | --- | --- |
| found before solving | `checks.run_checks` | 9.1.2 |
| conflict *n* of *N*: the rules | deletion-filter loop, then `describe` | 9.1.3, 9.1.5, 9.1.6 |
| why | `arithmetic`: every start-year combination | 9.1.6 |
| ways out of this conflict | `remedy` on each changeable rule | 9.1.6 |
| the cheapest repair, checked | elastic model, then a solve of the repaired scenario | 9.1.4 |

| Rule kind | Sentence pattern |
| --- | --- |
| must-do | "*P* is must-do: it has to start in *years*." |
| override | "Planners forced *P* into the plan[, starting in *year*]." |
| precedence | "*child* may start in *t* only if *parent* has started by *t − L*." |
| budget | "Finance locked the *y* budget at *$B* (GridCap's figure: *$B₀*)." |
| crews | "*Program* crews have *K* crew-months in *y*[ in this scenario (GridCap's figure: *K₀*)]." |

**Further reading:** OR-Tools,
[MathOpt](https://developers.google.com/optimization/math_opt), whose infeasibility analysis
returns a conflict as named rows and bounds (lesson 4.3.5 reads that result type), the input a
translator like this one reads. Gurobi's
[infeasibility example tour](https://docs.gurobi.com/projects/examples/en/current/overview/infeasibility.html),
whose `workforce1` example computes an IIS for the user to inspect. That is the step this lesson
starts from, not the message to stop at. Pyomo's
[Infeasibility Diagnostics](https://pyomo.readthedocs.io/en/stable/explanation/analysis/iis.html),
which separates "repair options" from the minimal system as this message does.

## Challenges

1. Add a sentence for `floor_Coast` that also gives the region's total spend in the repaired plan.
   Which function needs the plan, and why can `describe` not get it?
2. The two override conflicts repeat three of their four rules. Rewrite `explain` so that a message
   with several conflicts lists shared rules once and says which conflicts they belong to.
3. A conflict with five projects of three start years each has 243 combinations. Change
   `arithmetic` to show only the combination that misses by the least.

## Design Note: The Translator Is a Table, Kept Next to the Model

`describe` and `remedy` know every kind of row the model builds, and nothing else. When a new rule
family enters the model (a regional cap, a vendor limit), its name pattern, its sentence and its
remedy have to enter the translator in the same change, or the message falls back to the raw row
name. A test that builds every kind of row and checks that `describe` never returns the name
itself catches the gap. The module's tests check the weaker version: the message for P017 contains
no row name.

## The Full Programs

Each snippet above is part of a complete program, and each program printed the output the lesson
shows. Open one to read it whole, change it, and run it again: Run starts the program on your copy
of the code, so the course's own files never change.

**lock_message.py.** The whole Budget Lock message: the check, three conflicts with their
arithmetic and ways out, and the cheapest repair checked by a solve (*every section*). *Try:* Take
P023's override out of `LOCK`. Predict how many conflicts the message reports.

- Program: [lock_message.py](src/lock_message.py)

The translator is a library, and the message also uses the checks, the filters and the elastic
model of the earlier lessons.

- Library: [message.py](src/message.py)
- Library: [checks.py](src/checks.py)
- Library: [filters.py](src/filters.py)
- Library: [elastic.py](src/elastic.py)
