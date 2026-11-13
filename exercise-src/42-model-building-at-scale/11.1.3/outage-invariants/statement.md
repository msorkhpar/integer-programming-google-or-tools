A grid operator (fictional) generates planned-outage schedules for testing its maintenance
scheduler: thousands of schedules from different seeds. Before any of them reaches the scheduler,
each is checked against the rules every schedule must keep. An outage takes a site out of service
for `weeks` consecutive weeks from `start_week`, and needs `crew` crews in each of those weeks.

Write `violations(outages, crews_per_week)` in `outages.py`. It returns a list of strings, one per
broken rule, each starting with the rule's name and a colon; a schedule that keeps every rule gives
an empty list. The rules and the lines they produce:

| Rule | Broken when | Line |
| --- | --- | --- |
| unique ids | an id is used by more than one outage | `unique ids: O1`, once per such id |
| inside the year | an outage lasts no week, starts before week 1, or runs past week 52 | `inside the year: O7` |
| one outage per site | two outages at one site are out in a common week | `one outage per site: O1 and O2`, smaller id first |
| crews suffice | the outages active in a week need more than `crews_per_week` crews | `crews suffice: week 12 needs 5`, by week |

`active_weeks(o)` gives the weeks an outage is out. The lines come in the table's order: the
`unique ids` lines first (ids sorted), then the `inside the year` lines in the order the outages are
listed, then the `one outage per site` lines (by the list position of the pair's smaller-id outage,
then of the other), then the `crews suffice` lines by week, earliest first. Ids are compared as
strings, so "smaller id first" puts `O10` before `O2`; two outages sharing one id are left to the
unique-ids rule. The crews rule counts every week an outage is active, including the weeks past 52
of an outage that also breaks "inside the year".

The tests check the rule names, the full line for the crews rule and for duplicate ids, and the full
list for one schedule that breaks every rule. About fifteen lines.
