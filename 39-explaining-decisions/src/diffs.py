"""Scenario diffs: what changed between two runs, in plan, money and inputs (lesson 9.3.3)."""

from __future__ import annotations

from dataclasses import dataclass

from explain_model import Run, real_spend


@dataclass
class Diff:
    selected: list[str]                       # in b's plan, not in a's
    deferred: list[str]                       # in a's plan, not in b's
    shifted: list[tuple[str, int, int]]       # in both, with a different start: (project, a's year, b's year)
    npv: float                                # b's NPV less a's, $k
    spend: dict[int, int]                     # b's spend less a's, per year, $k


def diff_scenarios(a: Run, b: Run) -> Diff:
    """Compare two runs project by project: never variable by variable, never by position in a list."""
    pa, pb = a.plan, b.plan
    sa, sb = real_spend(a.built.portfolio, pa), real_spend(b.built.portfolio, pb)
    return Diff(
        selected=sorted(set(pb) - set(pa)),
        deferred=sorted(set(pa) - set(pb)),
        shifted=[(p, pa[p], pb[p]) for p in sorted(set(pa) & set(pb)) if pa[p] != pb[p]],
        npv=b.npv - a.npv,
        spend={y: sb[y] - sa[y] for y in sa},
    )


def input_changes(a: dict, b: dict, where: str = "") -> list[str]:
    """Every input that differs between two scenarios' inputs, as 'key: old -> new'."""
    found = []
    for key in sorted(set(a) | set(b)):
        old, new = a.get(key, "absent"), b.get(key, "absent")
        if isinstance(old, dict) and isinstance(new, dict):
            found += input_changes(old, new, f"{where}{key}.")
        elif old != new:
            found.append(f"{where}{key}: {old} -> {new}")
    return found


def show(d: Diff) -> list[str]:
    """The diff as lines a planner reads first."""
    earlier = [f"{p} {s}->{t}" for p, s, t in d.shifted if t < s]
    later = [f"{p} {s}->{t}" for p, s, t in d.shifted if t > s]
    return [f"selected  {d.selected}",
            f"deferred  {d.deferred}",
            f"shifted earlier {earlier}",
            f"shifted later   {later}",
            f"NPV change ${d.npv:+,.0f}k",
            "spend change by year " + ", ".join(f"{y}: {v:+,}" for y, v in d.spend.items())]
