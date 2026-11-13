"""A Hypothesis strategy for water-main selection instances that always have a valid plan.

An instance is a dict:
    "cost":   {project: (capital $k, operating $k)}
    "budget": (capital budget $k, operating budget $k)
    "must":   [projects that must be funded]
    "needs":  {project: [its prerequisites]}, every project a key
    "value":  {project: value}
"""

from __future__ import annotations

from hypothesis import strategies as st


@st.composite
def instances(draw) -> dict:
    # TODO: draw a valid plan first, then build the data around it.
    return {"cost": {}, "budget": (0, 0), "must": [], "needs": {}, "value": {}}

if __name__ == "__main__":
    print(instances().example())
