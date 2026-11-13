"""What GridCap's sizes put into the timing model: projects and relationships in, rows and nonzeros out.

The counts come from the tables and from the matrix builder's entries, family by family, so they
show which part of the data each part of the model grows with. GridCap is fictional.
"""

from __future__ import annotations

from gridcap import generate
from matrix_builder import columns, entries
from tables import tables_of

if __name__ == "__main__":
    print(f"{'size':7}{'projects':>9}{'must':>6}{'child':>7}{'groups':>7}{'starts':>8}"
          f"{'once':>7}{'alt':>5}{'after':>7}{'budget':>7}{'nonzeros':>10}{'budget nz':>11}")
    for size in ("tiny", "small", "medium", "large"):
        t = tables_of(generate(size))
        cols = columns(t)
        rows, terms = entries(cols, t)
        family = rows.assign(family=rows["name"].str.split("_").str[0])
        count = family["family"].value_counts()
        budget_rows = family.loc[family["family"] == "budget", "row"]
        p = t.projects
        print(f"{size:7}{len(p):>9,}{int(p['must_do'].sum()):>6,}{int((p['parent'] != '').sum()):>7,}"
              f"{p.loc[p['alt_group'] != '', 'alt_group'].nunique():>7,}{len(cols):>8,}"
              f"{count.get('once', 0) + count.get('must', 0):>7,}{count.get('alt', 0):>5,}{count.get('after', 0):>7,}"
              f"{count.get('budget', 0):>7,}{len(terms):>10,}{int(terms['row'].isin(budget_rows).sum()):>11,}")
