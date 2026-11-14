"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from constant import constant_dollar_value

forecast = {2030: -1500, 2031: 400, 2032: 450, 2033: 500, 2034: 550}

print("nominal 7%, inflation 0%:", round(constant_dollar_value(forecast, 0.07, 0.0, 2030), 3))
print("nominal 7%, inflation 2.5%:", round(constant_dollar_value(forecast, 0.07, 0.025, 2030), 3))
print("nominal 10%, inflation 2.5%:", round(constant_dollar_value(forecast, 0.10, 0.025, 2030), 3))
