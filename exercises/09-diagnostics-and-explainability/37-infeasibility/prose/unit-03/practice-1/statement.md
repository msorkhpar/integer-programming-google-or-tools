A school's timetabling model has two kinds of rules. **Hard** rules are physics and law: a room
holds one class at a time, a teacher works at most six periods. **Soft** rules are requests
someone made and could withdraw: "7A only in the mornings", "the lab is closed on Tuesday". When
the timetable has no solution, the deputy head wants a conflict made of soft rules only, the ones
a person can change, read together with every hard rule.

You get an oracle, `infeasible(rules) -> bool`, which says whether the timetable has no solution
when exactly the rules in the set `rules` are switched on. Write `conflict_among(soft, hard,
infeasible)`:

- if all the rules together are feasible, return `None`;
- if the hard rules alone are already infeasible, return `[]` (no soft rule is to blame);
- otherwise run a deletion filter over the soft rules, in the order given, with every hard rule
  switched on in every question, and return the soft rules that are left, in the order given.

What is left must be irreducible among the soft rules: with the hard rules on, the kept soft
rules are infeasible, and dropping any one of them makes them feasible. About twelve lines.
