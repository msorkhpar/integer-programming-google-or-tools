The asset-health team sends its register as CSV, and every cell arrives as text. The risk model of
lesson 1.1.2 computes each asset's probability of having failed by age $`t`$ as
$`F(t) = 1 - e^{-(t/\eta)^{\beta}}`$, which only makes sense for a shape $`\beta > 0`$ and a scale
$`\eta > 0`$. Give the register a type, so a bad row is caught here and not inside the model.

In `assets.py`, give `AssetRow` its real fields, and write `parse_assets(rows)`. `rows` is a list of
dicts of strings, one per CSV row. It returns the valid rows as `AssetRow` objects, in order, and a
list of `(index, field)` pairs, one per invalid row, where `index` is the row's position in `rows`
and `field` the name of the field that failed. Each invalid row in the tests has one bad field.

| field | type | rule |
| --- | --- | --- |
| `asset_id`, `kind` | text | any |
| `region` | text | one of `North`, `South`, `East`, `West` |
| `age` | whole years | 0 or more |
| `weibull_beta` ($`\beta`$) | number | above 0 |
| `weibull_eta` ($`\eta`$, years) | number | above 0 |
| `rul` | whole years | 0 or more |
| `cof` | whole $k | 0 or more |

A value that would need a guess to read, such as `"1,800"`, is invalid.

About twelve lines.
