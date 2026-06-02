"""Test configuration — loads .env.test and provides the shared Client fixture."""

import os

import pytest
from dotenv import load_dotenv

from awsysco import Client
from awsysco.exceptions import AwsysForbiddenError

# Load staging credentials from .env.test (gitignored)
load_dotenv(".env.test")

# Messages that indicate a staging account restriction rather than a code bug
_SKIP_MESSAGES = (
    "email verification required",
    "email not verified",
)


@pytest.fixture(scope="session")
def client() -> Client:
    """Return a Client pointed at the staging environment."""
    api_key = os.environ.get("AWSYS_API_KEY")
    if not api_key:
        pytest.skip("AWSYS_API_KEY not set — copy .env.example to .env.test")

    base_url = os.environ.get("AWSYS_BASE_URL", "https://staging.awsys.co")
    return Client(api_key=api_key, base_url=base_url)


@pytest.fixture(autouse=True)
def skip_on_account_restriction(request):
    """Skip integration tests that fail due to staging account restrictions
    (e.g. email verification required) rather than code bugs.
    """
    yield
    # Nothing to do post-yield — we catch before yield via try/except below


def pytest_runtest_call(item):
    """Hook: convert AwsysForbiddenError 'email verification required' into a skip."""
    try:
        item.runtest()
    except AwsysForbiddenError as exc:
        msg = str(exc).lower()
        if any(phrase in msg for phrase in _SKIP_MESSAGES):
            pytest.skip(f"Staging account restriction: {exc}")
        raise
