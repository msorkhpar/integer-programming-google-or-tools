import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def pytest_configure(config):
    # Starlette 1.10 warns that its TestClient will move from httpx to httpx2; the client works the same.
    config.addinivalue_line("filterwarnings", "ignore:Using `httpx` with `starlette.testclient`")
