"""Three requests at once to a path that blocks for one second: declared `async def`, then `def`.

`time.sleep(1)` stands in for any blocking call, a solve included: it holds its thread and never
awaits. The TestClient runs the app on one event loop, as a server process does.
"""

import threading
import time
import warnings

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient` is deprecated")
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

app = FastAPI()


@app.get("/async-solve")
async def async_solve() -> dict:
    time.sleep(1)           # blocks the event loop: nothing else runs meanwhile
    return {"done": True}


@app.get("/def-solve")
def def_solve() -> dict:
    time.sleep(1)           # FastAPI runs a def path in its threadpool, so the loop stays free
    return {"done": True}


def three_at_once(client: TestClient, path: str) -> float:
    calls = [threading.Thread(target=client.get, args=(path,)) for _ in range(3)]
    start = time.perf_counter()
    for call in calls:
        call.start()
    for call in calls:
        call.join()
    return time.perf_counter() - start


with TestClient(app) as client:
    for path in ("/async-solve", "/def-solve"):
        print(f"3 requests to {path:<13} took {three_at_once(client, path):.0f} s")
