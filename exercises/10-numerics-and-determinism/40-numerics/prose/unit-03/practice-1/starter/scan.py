from __future__ import annotations

KINDS = {"(bound viol.)": "bound", "(int. viol.)": "integrality", "(row viol.)": "row"}


def scan(lines: list[str], max_span: float = 1e6) -> list[str]:
    """The numerical findings of a HiGHS log, in the order their lines appear."""
    findings: list[str] = []
    # TODO: warnings, a matrix span above max_span, and violations above 0.
    return findings


if __name__ == "__main__":
    print(scan(["WARNING: Problem has some excessively large costs", "  Matrix  [1e-01, 1e+09]",
                "                    8.89e-07 (int. viol.)"]))
