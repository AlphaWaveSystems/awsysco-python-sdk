"""Unit tests for client configuration: env fallback, validation, redaction, User-Agent."""

from __future__ import annotations

import re
import warnings

import pytest

import awsysco
import awsysco._http
import awsysco.client
from awsysco import AsyncClient, Client
from awsysco.exceptions import AwsysConfigurationError


@pytest.fixture(autouse=True)
def _reset_one_shot_warning_flags(monkeypatch):
    """The non-awsys-key and plain-http warnings are one-shot per process —
    reset the module-level flags around every test so each test's expectations
    don't depend on collection order."""
    monkeypatch.setattr(awsysco.client, "_warned_non_awsys_key", False)
    monkeypatch.setattr(awsysco._http, "_warned_http_base_url", False)


class TestApiKeyResolution:
    def test_explicit_api_key_used(self):
        client = Client(api_key="awsys_explicit")
        assert client._http.redacted_key.endswith("icit")

    def test_env_fallback(self, monkeypatch):
        monkeypatch.setenv("AWSYS_API_KEY", "awsys_from_env")
        client = Client()
        assert client._http.redacted_key.endswith("_env")

    def test_missing_key_raises_configuration_error(self, monkeypatch):
        monkeypatch.delenv("AWSYS_API_KEY", raising=False)
        with pytest.raises(AwsysConfigurationError):
            Client()

    def test_non_awsys_prefixed_key_warns(self, monkeypatch):
        monkeypatch.delenv("AWSYS_API_KEY", raising=False)
        with pytest.warns(UserWarning, match="does not look like"):
            Client(api_key="sk-not-an-awsys-key")

    def test_non_awsys_prefixed_key_warns_only_once_per_process(self, monkeypatch):
        monkeypatch.delenv("AWSYS_API_KEY", raising=False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Client(api_key="sk-not-an-awsys-key")
            Client(api_key="sk-also-not-awsys")
        assert len(caught) == 1


class TestBaseUrlResolution:
    def test_env_fallback(self, monkeypatch):
        monkeypatch.setenv("AWSYS_BASE_URL", "https://staging.awsys.co")
        client = Client(api_key="awsys_x")
        assert client._http.base_url == "https://staging.awsys.co"

    def test_default_base_url(self, monkeypatch):
        monkeypatch.delenv("AWSYS_BASE_URL", raising=False)
        client = Client(api_key="awsys_x")
        assert client._http.base_url == "https://awsys.co"

    def test_strips_trailing_slash(self):
        client = Client(api_key="awsys_x", base_url="https://awsys.co/")
        assert client._http.base_url == "https://awsys.co"

    def test_rejects_missing_scheme(self):
        with pytest.raises(AwsysConfigurationError):
            Client(api_key="awsys_x", base_url="awsys.co")

    def test_warns_on_plain_http(self):
        with pytest.warns(UserWarning, match="unencrypted"):
            Client(api_key="awsys_x", base_url="http://awsys.co")

    def test_warns_on_plain_http_only_once_per_process(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            Client(api_key="awsys_x", base_url="http://awsys.co")
            Client(api_key="awsys_x", base_url="http://also-awsys.co")
        assert len(caught) == 1


class TestRedaction:
    def test_client_repr_never_contains_full_key(self):
        client = Client(api_key="awsys_supersecretvalue")
        assert "supersecretvalue" not in repr(client)
        assert "alue" in repr(client)

    def test_async_client_repr_never_contains_full_key(self):
        client = AsyncClient(api_key="awsys_supersecretvalue")
        assert "supersecretvalue" not in repr(client)

    def test_http_client_repr_never_contains_full_key(self):
        client = Client(api_key="awsys_supersecretvalue")
        assert "supersecretvalue" not in repr(client._http)

    def test_http_client_str_never_contains_full_key(self):
        """str() falls back to __repr__ for a plain (non-pydantic) class only if
        __str__ isn't independently defined — confirm that's actually true here,
        not assumed."""
        client = Client(api_key="awsys_supersecretvalue")
        assert "supersecretvalue" not in str(client._http)
        assert "supersecretvalue" not in f"{client._http}"

    def test_resource_object_repr_never_contains_full_key(self):
        """Every resource attached to the client (client.links, client.folders, …)
        must not leak the key either — even though none of them override __repr__,
        confirm the default object repr (class + id only) stays that way rather
        than assuming it can never regress (e.g. from a future __repr__ that
        dumps __dict__)."""
        client = Client(api_key="awsys_supersecretvalue")
        for name in ("links", "folders", "webhooks", "profile", "affiliate"):
            resource = getattr(client, name)
            assert "supersecretvalue" not in repr(resource)
            assert "supersecretvalue" not in str(resource)

    def test_async_http_client_str_never_contains_full_key(self):
        client = AsyncClient(api_key="awsys_supersecretvalue")
        assert "supersecretvalue" not in str(client._http)


class TestUserAgent:
    def test_user_agent_matches_contract_pattern(self):
        client = Client(api_key="awsys_x")
        ua = client._http._client.headers["User-Agent"]
        assert re.match(r"^awsysco-python-sdk/\d+\.\d+\.\d+", ua)

    def test_user_agent_version_matches_package_version(self):
        client = Client(api_key="awsys_x")
        ua = client._http._client.headers["User-Agent"]
        assert awsysco.__version__ in ua

    def test_pyproject_declares_dynamic_version_from_version_py(self):
        """The version has a single source of truth (awsysco/_version.py, read by
        hatchling via [tool.hatch.version].path) — pyproject.toml must declare
        `dynamic = ["version"]` and must NOT also hardcode a static `version =`
        under [project], or the two could drift out of sync again."""
        import pathlib

        pyproject = pathlib.Path(__file__).resolve().parents[1] / "pyproject.toml"
        text = pyproject.read_text()
        assert re.search(r'(?m)^dynamic\s*=\s*\[.*"version".*\]', text), (
            "pyproject.toml must declare dynamic = [\"version\"]"
        )
        project_section = text.split("[project]", 1)[1].split("\n[", 1)[0]
        assert not re.search(r'(?m)^version\s*=', project_section), (
            "pyproject.toml must not also hardcode a static version under [project] "
            "— that would reintroduce the dual-source-of-truth drift"
        )
        # The actual build→wheel-version resolution is verified manually (and via
        # the release checklist) with `python -m build` — not re-run here as a
        # subprocess on every unit-test invocation, to keep this suite fast.


class TestPerCallTimeout:
    def test_timeout_override_is_threaded_through(self, monkeypatch):
        client = Client(api_key="awsys_x")
        captured = {}

        def fake_request(method, path, **kwargs):
            captured.update(kwargs)

            class _Resp:
                status_code = 200
                content = b"{}"
                is_error = False

                def json(self):
                    return {}

            return _Resp()

        monkeypatch.setattr(client._http._client, "request", fake_request)
        client._http.get("/api/v1/me", timeout=5.0)
        assert captured["timeout"] == 5.0
