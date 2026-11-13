A port authority's LP plans berth time, cranes, pilots and dredging. Suppliers and the regulator
offer ways to relax some of its rows: extra crane-months, more budget, a waiver that lowers a
dredging requirement. Each offer has a cost. Finance wants the offers worth taking, ranked, using
the LP's shadow prices instead of a re-solve per offer.

Each offer relaxes one row of the LP, and is a dict with:

- `"price"`: the row's shadow price $`y`$, in value per row unit (negative for a requirement, a
  $`\ge`$ row, in a maximization);
- `"change"`: $`\Delta`$, how far one unit of the offer moves the row's right-hand side, in row units
  (a crane-month adds 440 $k of capacity; a waiver that lowers a requirement by 100 has
  $`\Delta = -100`$);
- `"cost"`: what one unit of the offer costs, in the same value units as the objective;
- `"units"`: how many units can be bought while the right-hand side stays inside the price's range.

Inside the range the price is exact, so the total net gain of an offer is

```math
\text{gain} = \text{units} \times \big(y \cdot \Delta - \text{cost}\big)
```

Write `worth_buying(offers)` in `relief.py`. Return a list of `(name, gain)` pairs for the offers
whose gain is positive, sorted by gain, largest first.

About eight lines.
