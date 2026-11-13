Planners want to see the trade-off before they pick a plan: how much NPV each extra $1k of risk
removed costs. Your milestone adds a frontier endpoint to the service. It answers with the plans the
epsilon-constraint method finds, from the plan with the most NPV to the plan that removes the most
risk, and never with a plan another returned plan beats on both counts. The practice portfolio is
invented for a fictional utility; each project carries, beside `npv`, a `risk` table: the risk it
removes ($k) for each start year, as milestone 3 computed it.

`frontier_endpoint.py` gives you milestone 2's model with a reduced rule set (`build`, `solve`,
`plan_of`, `check`), `objectives(snapshot, x)`, which returns the NPV and risk expressions,
`score(snapshot, plan)`, which returns `{"npv", "risk", "plan"}`, `from_json`, which turns a
snapshot's text year keys back into integers, and the request model `FrontierRequest` (a snapshot and
`points` from 2 to 11).

Write:

| function | contract | lesson |
| --- | --- | --- |
| `best(snapshot, first, then, floors)` | build a fresh model; add a row `value >= floor` for each entry of `floors` (`{"risk": 120}`); maximize `first` ("npv" or "risk"); if there is no plan return None; otherwise hold `first` at its optimum (a row `value >= optimum - HOLD`, with the given `HOLD = 1e-6`: the risk table is rounded to $0.001k, so an optimum need not be a whole number, and rounding it could cut off the optimum or let a worse plan in), maximize `then`, and return `score` of that plan | 8.3.1, 8.3.2 |
| `frontier(snapshot, points)` | the two ends, `best(.., "npv", "risk", {})` and `best(.., "risk", "npv", {})`; then, for k from 0 to `points - 1`, the floor `r_npv + (r_risk - r_npv) * k / (points - 1)` between the ends' risk values, and `best(.., "npv", "risk", {"risk": floor})`. Keep each point once: a point with the same NPV and the same risk removed as one already found is not added, even if its plan differs, so the first one found (the lowest floor) stays. Then drop any point another point beats or equals on both objectives, and sort by risk removed | 8.3.1, 8.3.3 |
| `create_app()` | a FastAPI app with `POST /frontier`, body `FrontierRequest`, answering `{"objectives": ["npv", "risk"], "points": frontier(...)}` with the snapshot passed through `from_json` | 12.4.1, 12.4.3 |

The lesson's service also answers with a `snapshot` field, because its request names a snapshot
already stored, by digest, and the answer echoes that digest. Here the request carries the whole
snapshot, so the answer has only `objectives` and `points`.

The tests compare your points with every plan of the test portfolio, enumerated by brute force, so
any correct formulation passes. Each solve is exact (zero gap). About thirty-five lines.
