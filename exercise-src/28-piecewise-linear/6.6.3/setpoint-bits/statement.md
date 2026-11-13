A district heating network runs its supply water at one of a few fixed temperature setpoints; the
boiler controls cannot hold anything in between. For each setpoint the operator knows the pumping
power the network then needs. They are given as two lists, `temps` (°C) and `powers` (kW), with
`temps[i]` and `powers[i]` belonging together:

| Setpoint | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Temperature (°C) | 70 | 75 | 80 | 85 | 90 | 95 | 100 | 105 |
| Pumping power (kW) | 420 | 360 | 310 | 300 | 330 | 390 | 470 | 560 |

The model in `setpoints.py` has a continuous `temp` and a continuous `power`. Write
`add_setpoint(model, temp, power, temps, powers)` so that the model allows exactly the pairs
`(temp, power)` that are one of the listed setpoints: no blend of two setpoints, and no setpoint's
temperature with another's power. The network's full model already has hundreds of binaries, so
use **at most $`\lceil \log_2 n \rceil`$ binary variables** for $`n`$ setpoints: three for eight.
Add whatever continuous variables you need.

With $`i = 0, \dots, n - 1`$ the setpoints, $`T_i`$ and $`P_i`$ their temperature and power, the
model so far is

```math
\begin{aligned}
& t, \; p \in \mathbb{R} && && \text{(supply temperature, °C; pumping power, kW)} \\
& \text{?} && && \text{(at most } \lceil \log_2 n \rceil \text{ binaries, and your rows)}
\end{aligned}
```

This is not a curve: no two setpoints may be mixed, not even neighbours. Think about what that
changes in the logarithmic form's rows, and whether the order of the codes still matters.

The tests fix the temperature and the power and ask the solver whether the model accepts the pair;
one test also counts the model's integer variables. Any correct formulation within the binary limit
passes. About ten lines.
