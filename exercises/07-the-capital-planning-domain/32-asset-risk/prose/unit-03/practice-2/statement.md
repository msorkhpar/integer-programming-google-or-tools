A gas utility keeps a register of its line valves. For each valve it has the age today, the
Weibull curve of its type (`beta`, `eta` in years) and the cost of one failure `cof` ($k). Each
valve in the register is working today. A failed valve is replaced, so the register uses the
chance of *at least one* failure in the coming year, as in lesson 1.1.2. That is why this practice
uses PoF although the lesson counts expected failures from its last rule on: the expected count is
for an asset that is repaired and kept, and can fail again in the same year, while a valve that
fails here is replaced, not repaired, so the question is whether it fails at all.

Write two functions in `register.py`:

- `risk(v)`: valve `v`'s expected failure cost in the coming year, $k;
- `rank_by_risk(valves)`: the valves' ids, highest risk first.

Write the risk as a formula in the lesson's notation first. The tests compute each valve's chance
of failing with `scipy.stats.weibull_min`. About five lines.
