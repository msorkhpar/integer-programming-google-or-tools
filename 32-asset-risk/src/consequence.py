"""A consequence of failure built from its parts, for one invented substation transformer.

Every number below is made up for the lesson, like the rest of GridCap.
"""

CUSTOMERS_SERVED = 120_000       # all the customers of the (fictional) utility
customers_out = 4_200            # customers the transformer feeds
hours_out = 6.0                  # hours until they are switched to another source
cost_per_customer_hour = 0.025   # $k a customer loses per hour without power
repair = 380                     # $k: emergency crew, a spare unit, overtime
safety = 0.002 * 50_000          # chance of an injury times its cost, $k
environment = 0.10 * 300         # chance of an oil spill times its clean-up, $k

interruption = customers_out * hours_out * cost_per_customer_hour
cof = repair + interruption + safety + environment
print(f"repair ${repair:,.0f}k + interruption ${interruption:,.0f}k + safety ${safety:,.0f}k "
      f"+ environment ${environment:,.0f}k = CoF ${cof:,.0f}k")

saifi = customers_out / CUSTOMERS_SERVED
saidi = customers_out * hours_out * 60 / CUSTOMERS_SERVED
print(f"one failure adds {saifi:.3f} interruptions per customer (SAIFI) "
      f"and {saidi:.1f} minutes per customer (SAIDI)")
