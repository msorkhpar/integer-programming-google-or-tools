A planning team's dashboard shows every solve's gap, and finance asked why HiGHS and SCIP runs of
the same scenario report slightly different percentages. Write `gap_report(primal, dual)` in
`gaps.py`. `primal` is the incumbent's objective value (infinite, with either sign, when no plan was
found) and `dual` is the best bound. It returns a dict with three entries:

- `"absolute"`: the distance between the two numbers, never negative;
- `"relative_highs"`: the absolute gap divided by the size of the incumbent;
- `"relative_scip"`: the absolute gap divided by the smaller of the two numbers in size.

When there is no plan, every entry is `None`. A relative gap whose divisor is zero is `None` too:
a dashboard must not show a made-up number. When there is a plan but no bound has been proved yet
(`dual` infinite, with either sign), the gap is not unknown but unbounded: the absolute gap is
`math.inf`, and so is each relative gap whose divisor is not zero. The function works for maximizations and
minimizations alike. About ten lines.
