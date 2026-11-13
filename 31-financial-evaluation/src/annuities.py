"""An annuity's present value three ways, the annuity due, the perpetuity, and the payment back."""

import numpy_financial as npf

from finance import annuity_factor, present_value

payment, years, rate = 100, 20, 0.07
loop = present_value({y: payment for y in range(1, years + 1)}, rate, 0)
closed = payment * annuity_factor(rate, years)
rows = [
    ("sum of 20 discounted payments", loop),
    ("closed form A(1 - (1+r)^-n)/r", closed),
    ("npf.pv(0.07, 20, -100)", npf.pv(rate, years, -payment)),
    ("payments at the start of each year", npf.pv(rate, years, -payment, when="begin")),
    ("closed form times 1.07", closed * 1.07),
    ("forever (perpetuity) A / r", payment / rate),
    ("npf.pmt(0.07, 20, 1000)", npf.pmt(rate, years, 1_000)),
    ("1000 / annuity factor", 1_000 / annuity_factor(rate, years)),
]
for label, value in rows:
    print(f"{label:36}{value:9.2f}")
