"""The two numbers per project that GridCap's generator drew to build its NPV table.

`gridcap.generator._with_npv` draws, for every project, a benefit ratio (benefit over capex,
1.15 + 0.9u) and a decay (value lost per year of delay, 0.03 + 0.05u), uses them, and keeps only
the resulting NPVs. A real finance team hands you these as a benefit forecast; here we replay the
generator and record each draw as it is made. The portfolio itself is unchanged.
"""

from __future__ import annotations

import gridcap.generator as generator
from gridcap import DEFAULT_SEED, Portfolio


def benefit_assumptions(size: str, seed: int = DEFAULT_SEED) -> tuple[Portfolio, dict[str, tuple[float, float]]]:
    """(portfolio, {project id: (benefit ratio, decay)}) for one GridCap size."""
    found: dict[str, tuple[float, float]] = {}
    original = generator._with_npv

    def recording(draw, project, years):
        units: list[float] = []

        class Recorder:
            def unit(self) -> float:
                u = draw.unit()
                units.append(u)
                return u

        out = original(Recorder(), project, years)
        found[project.project_id] = (1.15 + 0.9 * units[0], 0.03 + 0.05 * units[1])
        return out

    generator._with_npv = recording
    try:
        portfolio = generator.generate(size, seed)
    finally:
        generator._with_npv = original
    return portfolio, found
