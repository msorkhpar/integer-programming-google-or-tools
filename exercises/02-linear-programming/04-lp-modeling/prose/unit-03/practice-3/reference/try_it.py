"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from carry import plan_spending

def r(v):
    return v if v is None else round(v, 2)


budgets = {2040: 80, 2041: 80, 2042: 80}
work = {2040: 40, 2041: 110, 2042: 100}
value = {2040: 1.2, 2041: 1.0, 2042: 0.7}

for max_carry in (0.5, 0.1):
    status, total, spend, carry = plan_spending(budgets, work, value, max_carry)
    print(f"max carry {max_carry}:", status, r(total))
    print(f"  spend at max carry {max_carry}:", spend and {y: r(s) for y, s in spend.items()})
    print(f"  carry at max carry {max_carry}:", carry and {y: r(c) for y, c in carry.items()})
