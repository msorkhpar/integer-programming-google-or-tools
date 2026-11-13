import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fake_aws import FAKE_CREDENTIALS  # noqa: E402


@pytest.fixture(autouse=True)
def aws_credentials(monkeypatch):
    """moto's fake credentials for every test; no test can sign a request as anyone real."""
    for name, value in FAKE_CREDENTIALS.items():
        monkeypatch.setenv(name, value)
