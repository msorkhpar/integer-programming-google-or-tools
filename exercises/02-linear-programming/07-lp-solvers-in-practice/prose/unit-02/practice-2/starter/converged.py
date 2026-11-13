from __future__ import annotations


def table_rows(log: list[str]) -> list[tuple[int, float, float, float]]:
    """Each PDLP progress row as (iteration, rel_prim_res, rel_dual_res, rel_gap)."""
    # TODO: keep the lines whose text before the first "|" starts with an iteration number,
    # and read the three numbers between the first and second "|".
    return []


def converged_at(log: list[str], tol: float) -> int | None:
    """The first reported iteration where all three relative measures are within `tol`, or None."""
    # TODO
    return -1


if __name__ == "__main__":
    demo = [" iter# kkt_pass   time | rel_prim_res rel_dual_res      rel_gap |   prim_resid",
            "     0      0.0    0.0 |  1.00000e-01     0.500000      0.00000 |      3.00000",
            "    64     65.0    0.0 |  2.00000e-07  3.00000e-07 -4.00000e-07 |  0.000100000"]
    print(table_rows(demo), converged_at(demo, 1e-6))
