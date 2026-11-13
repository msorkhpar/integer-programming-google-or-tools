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
    names = [f"w{k}" for k in range(1, draw(st.integers(1, 6)) + 1)]
    cost, needs, value, chosen = {}, {}, {}, set()
    for k, name in enumerate(names):
        cost[name] = (draw(st.integers(1, 40)), draw(st.integers(1, 10)))
        value[name] = draw(st.integers(1, 20))
        earlier = names[:k]
        needs[name] = draw(st.lists(st.sampled_from(earlier), unique=True, max_size=2)) if earlier else []
        if all(q in chosen for q in needs[name]) and draw(st.booleans()):
            chosen.add(name)
    must = [p for p in names if p in chosen and draw(st.booleans())]
    capital = sum(cost[p][0] for p in chosen) + draw(st.integers(0, 30))
    operating = sum(cost[p][1] for p in chosen) + draw(st.integers(0, 8))
    return {"cost": cost, "budget": (capital, operating), "must": must, "needs": needs, "value": value}


if __name__ == "__main__":
    print(instances().example())
