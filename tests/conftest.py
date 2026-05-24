"""Test configuration — loads .env.test and provides the shared Client fixture."""

import os

import pytest
from dotenv import load_dotenv

from awsysco import Client

# Load staging credentials from .env.test (gitignored)
load_dotenv(".env.test")


@pytest.fixture(scope="session")
def client() -> Client:
    """Return a Client pointed at the staging environment."""
    api_key = os.environ.get("AWSYS_API_KEY")
    if not api_key:
        pytest.skip("AWSYS_API_KEY not set — copy .env.example to .env.test")

    base_url = os.environ.get("AWSYS_BASE_URL", "https://staging.awsys.co")
    return Client(api_key=api_key, base_url=base_url)
