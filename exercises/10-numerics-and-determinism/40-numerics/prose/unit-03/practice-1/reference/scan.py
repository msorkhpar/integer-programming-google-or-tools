from __future__ import annotations

KINDS = {"(bound viol.)": "bound", "(int. viol.)": "integrality", "(row viol.)": "row"}


def scan(lines: list[str], max_span: float = 1e6) -> list[str]:
    """The numerical findings of a HiGHS log, in the order their lines appear."""
    findings: list[str] = []
    for line in lines:
        text = line.strip()
        if text.startswith("WARNING:"):
            findings.append("warning: " + text[len("WARNING:"):].strip())
        elif text.startswith("Matrix"):
            low, high = (float(v) for v in text[text.index("[") + 1:text.index("]")].split(","))
            if high / low > max_span:
                findings.append(f"matrix span {high / low:.0e}")
        else:
            for marker, kind in KINDS.items():
                value = text.split()[0] if text.endswith(marker) else None
                if value is not None and float(value) > 0:
                    findings.append(f"{kind} violation {value}")
    return findings


if __name__ == "__main__":
    print(scan(["WARNING: Problem has some excessively large costs", "  Matrix  [1e-01, 1e+09]",
                "                    8.89e-07 (int. viol.)"]))
