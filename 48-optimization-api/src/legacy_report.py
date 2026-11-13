"""A worker with a hidden hazard: a report helper that imports PuLP before the job solves.

Imported only by crash_isolation.py, in a child process. In the runner, a process that has imported
pulp is killed by SIGSEGV on its first HiGHS MIP solve through MathOpt (lesson 5.2.1). The service's own code never imports pulp.
"""

import pulp  # noqa: F401  (imported first, as the report helper's module did)

from jobs import JobRequest, Outcome, run_job


def run_job_with_pulp_report(request: JobRequest) -> Outcome:
    return run_job(request)
