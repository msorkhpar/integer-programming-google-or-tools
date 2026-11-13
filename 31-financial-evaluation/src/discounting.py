"""Discount factors, and what one future payment is worth today, at GridCap's 7% and two other rates."""

from finance import discount_factor, escalate

print("years ahead     3%      7%     10%")
for n in (0, 1, 2, 3, 5, 10, 20, 30):
    print(f"{n:>10}  {discount_factor(0.03, n):.4f}  {discount_factor(0.07, n):.4f}  {discount_factor(0.10, n):.4f}")

payment, rate = 1_000, 0.07
today = payment * discount_factor(rate, 2030 - 2027)
print(f"$1,000k paid in 2030 is worth ${today:,.2f}k at the start of 2027")
print(f"${today:,.2f}k invested at 7% for 3 years grows to ${escalate(today, rate, 3):,.2f}k")
