"""Moto's stand-in for AWS, used by every program of this module.

Nothing here reaches AWS. The credentials are moto's documented fakes, set before any client is
made, so a call that escaped the mock could not sign as anyone. The account id moto reports is its
own placeholder, 123456789012. GridCap is a fictional utility.
"""

from __future__ import annotations

import os

from moto import mock_aws

FAKE_CREDENTIALS = {
    "AWS_ACCESS_KEY_ID": "testing",
    "AWS_SECRET_ACCESS_KEY": "testing",
    "AWS_SECURITY_TOKEN": "testing",
    "AWS_SESSION_TOKEN": "testing",
    "AWS_DEFAULT_REGION": "us-east-1",
}


def use_fake_credentials() -> None:
    """Point boto3 at moto's fake credentials, and at no config file on this machine."""
    os.environ.update(FAKE_CREDENTIALS)
    os.environ["AWS_CONFIG_FILE"] = os.devnull
    os.environ["AWS_SHARED_CREDENTIALS_FILE"] = os.devnull


def fake_aws():
    """A moto mock of every service. Batch jobs are not run in Docker: moto marks them SUCCEEDED."""
    use_fake_credentials()
    return mock_aws(config={"batch": {"use_docker": False}})
