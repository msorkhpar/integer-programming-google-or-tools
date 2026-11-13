from __future__ import annotations


def parse_row(line: str) -> dict | None:
    """One row of a HiGHS MIP progress table as a dict, or None if the line is not such a row."""
    if len(line) < 2 or line[0] != " ":
        return None
    fields = line[2:].split()
    if len(fields) != 12 or not fields[0].isdigit() or not fields[3].endswith("%"):
        return None
    src = line[1].strip()
    gap = None if fields[6] == "Large" else float(fields[6].rstrip("%")) / 100
    return {"src": src, "nodes": int(fields[0]), "bound": float(fields[4]), "incumbent": float(fields[5]),
            "gap": gap, "cuts": int(fields[7]), "lp_iters": int(fields[10])}


if __name__ == "__main__":
    print(parse_row(" R       0       0         0   0.00%   1520.5          1490               2.05%        0      0      0        16     0.1s"))
