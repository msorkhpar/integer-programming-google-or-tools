"""The same crashing job with the solve in a thread of the API's process: the whole service dies.

The service runs in a child process here, because the crash ends the process that has it.
GridCap is fictional.
"""

import os
import signal
import subprocess
import sys

SERVICE = """
import warnings
warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
import legacy_report                      # imports pulp first, as in crash_isolation.py
from fastapi.testclient import TestClient
from job_api import create_app
from jobs import JobStore
store = JobStore(worker=legacy_report.run_job_with_pulp_report)   # a thread pool, in this process
client = TestClient(create_app(store))
job_id = client.post("/jobs", json={"portfolio": "small"}).json()["job_id"]
store.get(job_id).future.exception()
print("poll ->", client.get(f"/jobs/{job_id}").json(), flush=True)
"""

done = subprocess.run([sys.executable, "-c", SERVICE], capture_output=True, text=True, env=os.environ)
print("the service printed:", done.stdout.strip() or "nothing")
print("service process:", f"killed by {signal.Signals(-done.returncode).name}" if done.returncode < 0
      else f"exit {done.returncode}")
