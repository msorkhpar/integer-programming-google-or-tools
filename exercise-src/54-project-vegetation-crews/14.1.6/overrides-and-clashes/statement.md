With calendars in place, GridCap's vegetation planner started using the plan every week, and wrote:

> Sometimes I know something the model doesn't. A crew is already on site near C17, so start it there
> in week 0. The county closes the road to C17 until October, so leave it. A landowner complained, so
> trim C02 first. I need to tell the planner these things and have it plan *around* them.
> And when it can't, "INFEASIBLE" is not an answer. Last week I forced in five circuits after a storm
> and got an empty plan and that one word. Tell me *which* of my decisions clash, in my words, so I
> know what to give up.

You start from the calendar scheduler of the lesson before. Take the planner's overrides: pin a
trim to a crew and a first week, skip a circuit, or force one in, each with a reason. Refuse an
override that names nothing before any model is built. When a season has no plan, name a smallest
set of the planner's rules that clash (the musts, the budget and the overrides, never the physics of
crews and weeks) in the planner's words, and print them in the report. Split the model out of
`planner.py` into `model.py`, and the explanation into `explain.py`.

**The explanation.** Name the rules in the order they are made: each must as its circuit comes in
the season, then the budget, then the overrides in the order given. The tests compare the
explanation with an exact tuple in that order.

**The report.** After the crew lines, a plan with an explanation prints
`these rules cannot all hold; change one of them:` and one line per rule, two spaces, `- ` and the
rule's words. An INFEASIBLE plan has no trims: its status line reads
`status INFEASIBLE: 0 trims, cost $0k, risk carried $0k`, and each crew's line shows only its weeks
off.

**`main.py`.** After the tiny season's report it prints two more sections, each after an empty line.
First the title `skip C03:` and the report of the tiny season with one override,
`Override("skip", "C03", reason="road closed")`. Then the title
`pin C01 and C05 a week apart on K1:` and the report with two,
`Override("pin", "C01", crew="K1", start=12, reason="crew is nearby")` and
`Override("pin", "C05", crew="K1", start=13, reason="landowner asked")`, which cannot both hold.
Keep the line that sets `planner.WORKERS = 1`.

Run's report gains the two sections above, as `expected/report.txt` shows. Submit runs every test in
`tests/`, the earlier steps' included, and compares Run's report with the expected one.
