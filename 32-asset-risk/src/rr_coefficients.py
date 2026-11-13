"""Risk-reduction coefficients rr[i, s] for some GridCap small projects, by start year."""

from risk_model import WINDOW, risk_coefficients
from gridcap import generate

small = generate("small")
rr = risk_coefficients(small)
plain = risk_coefficients(small, rate=0.0)
print(f"rr[i, s]: risk removed over {WINDOW} years from 2027, discounted at {small.discount_rate:.0%} ($k)")
for pid in ("P001", "P002", "P019", "P024", "P027", "P039"):
    p = small.project(pid)
    cells = "  ".join(f"{s}: {rr[pid, s]:>6,.0f} ({plain[pid, s]:>5,.0f})" for s in p.starts())
    print(f"{pid} {p.intervention:11} {p.duration}y | {cells}")
print("(in brackets: the same sum undiscounted)")
