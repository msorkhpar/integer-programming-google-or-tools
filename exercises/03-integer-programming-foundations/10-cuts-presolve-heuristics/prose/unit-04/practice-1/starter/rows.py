from __future__ import annotations


def parse_row(line: str) -> dict | None:
    """One row of a HiGHS MIP progress table as a dict, or None if the line is not such a row."""
    # TODO: the source is line[1]; split line[2:] into its 12 fields; check that it is a progress row;
    # convert the fields you return.
    return None


if __name__ == "__main__":
    print(parse_row(" R       0       0         0   0.00%   1520.5          1490               2.05%        0      0      0        16     0.1s"))
