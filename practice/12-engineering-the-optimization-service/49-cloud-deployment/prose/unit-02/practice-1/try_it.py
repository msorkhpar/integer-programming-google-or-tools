"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from trim_jobs import submit_trim


class FakeBatch:
    """Stands in for a boto3 Batch client: keeps each submit_job call and hands back an id."""

    def __init__(self):
        self.calls = []

    def submit_job(self, **kwargs):
        self.calls.append(kwargs)
        return {"jobId": f"job-{len(self.calls)}"}


batch = FakeBatch()
for plan_id, circuits in (("east/2033 draft", 320), ("_west 2034", 4200), ("all-regions", 9000)):
    job_id = submit_trim(batch, "plan-queue", "plan-solve:3", plan_id, circuits, 90)
    call = batch.calls[-1] if batch.calls else {}
    print(f"{plan_id!r}, {circuits} circuits -> {job_id}, name {call.get('jobName')!r}, "
          f"resources {call.get('containerOverrides', {}).get('resourceRequirements')}, timeout {call.get('timeout')}")
