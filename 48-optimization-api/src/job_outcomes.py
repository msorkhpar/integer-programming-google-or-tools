"""One job per way a solve can end, each mapped to its own status (lesson 12.4.2).

GridCap is fictional. The small portfolio's must-do P017 costs $5,310k in 2030 or 2031, so budgets
of $5,000k in both years leave no plan. Time-limited plans differ from run to run, so this program
prints their status and message shape, not their numbers.
"""

import re

from jobs import JobRequest, JobStore

store = JobStore()
asks = {
    "small, as given": JobRequest(portfolio="small"),
    "small, 2030-31 cut": JobRequest(portfolio="small", budget={2030: 5000, 2031: 5000}),
    "medium, 1 s limit": JobRequest(portfolio="medium", time_limit_s=1),
    "large, 1 s limit": JobRequest(portfolio="large", time_limit_s=1),
    "small, 2 threads": JobRequest(portfolio="small", highs_threads=2),
    "small, again": JobRequest(portfolio="small"),
}
ids = {label: store.submit(request) for label, request in asks.items()}
lines = []
for label, job_id in ids.items():
    job = store.get(job_id)
    outcome = store.outcome(job)        # waits for the job to finish
    message = re.sub(r"\$[\d,]+k", "$...k", re.sub(r"gap [\d.]+%", "gap ...%", outcome.message))
    lines.append(f"{label:<19} {outcome.status:<11} plan: {'yes' if outcome.starts else 'no ':<4} {message}")
print("\n".join(lines))
