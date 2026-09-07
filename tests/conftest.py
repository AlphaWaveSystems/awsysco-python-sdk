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


@pytest.hookimpl(wrapper=True)
def pytest_runtest_call(item):
    """Hook: convert AwsysForbiddenError 'email verification required' into a skip.

    Must be a hookwrapper (``yield`` around the real call) — a plain, non-wrapper
    ``pytest_runtest_call(item)`` that itself calls ``item.runtest()`` runs the test
    body a SECOND time, since pytest's own internal implementation still runs too.
    That was silently doubling every test's side effects (including live API calls
    against staging) prior to this fix.
    """
    try:
        return (yield)
    except AwsysForbiddenError as exc:
        msg = str(exc).lower()
        if any(phrase in msg for phrase in _SKIP_MESSAGES):
            pytest.skip(f"Staging account restriction: {exc}")
        raise


def pytest_collection_modifyitems(items):
    """Auto-apply the `integration` marker to any test using the `client` fixture.

    Keeps individual test files from having to remember `@pytest.mark.integration` —
    any test that asks for a live-staging `client` is, by definition, integration.
    """
    for item in items:
        if "client" in getattr(item, "fixturenames", ()):
            item.add_marker(pytest.mark.integration)
