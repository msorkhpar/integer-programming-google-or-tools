# 00-base: GridCap

GridCap is the course's running dataset: the capital portfolio of a **fictional** utility. It is
generated from a size and a seed and describes no real company.

```python
from gridcap import generate

tiny = generate("tiny")          # 8 projects, 3 years: small enough to check by hand
small = generate("small")        # 40 projects, 5 years
medium = generate("medium")      # 400 projects, 10 years
large = generate("large")        # 10,000 projects, 10 years, for performance work
```

| Object | What it holds |
| --- | --- |
| `Project` | program, region, asset, `cost_profile` (spend per year of work), `earliest_start`/`latest_start`, `must_do`, `parent` and `parent_lag`, `alt_group`, `crew_months`, `npv[start_year]` |
| `Asset` | kind, region, age, Weibull `weibull_beta`/`weibull_eta`, predicted `rul`, consequence of failure `cof` |
| `Portfolio` | `years`, `discount_rate`, `capital_budget` (one-period), `budget[year]`, `region_budget[(region, year)]`, `region_floor[region]`, `crews[(program, year)]` |

Money is in $k, as integers. `Portfolio.content_hash()` identifies a portfolio; `tests/` pins the
hash of every size, so a change to the generator is always deliberate.

```sh
python -m gridcap tiny --out data/tiny     # write the CSV files
python -m gridcap medium --hash            # print the content hash
```
