"""Unit tests for AsyncClient construction and resource wiring."""

from __future__ import annotations

import pytest

from awsysco import AsyncClient


class TestAsyncClientConstruction:
    def test_instantiates_without_error(self):
        client = AsyncClient(api_key="awsys_test")
        assert client is not None

    def test_has_links_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "links")

    def test_has_analytics_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "analytics")

    def test_has_qr_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "qr")

    def test_has_folders_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "folders")

    def test_has_bulk_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "bulk")

    def test_has_me_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "me")

    def test_has_tags_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "tags")

    def test_has_trust_score_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "trust_score")

    def test_has_data_export_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "data_export")

    def test_has_namespace_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "namespace")

    def test_has_utm_templates_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "utm_templates")

    def test_has_webhooks_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "webhooks")

    def test_has_saved_views_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "saved_views")

    def test_has_custom_domains_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "custom_domains")

    def test_has_agentlink_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "agentlink")

    def test_has_affiliate_resource(self):
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "affiliate")

    def test_qr_get_url_is_synchronous(self):
        """QR URL construction is sync even in AsyncClient."""
        client = AsyncClient(api_key="awsys_test", base_url="https://awsys.co")
        url = client.qr.get_url("abc123")
        assert "abc123" in url
        assert url.startswith("https://awsys.co")

    def test_custom_base_url(self):
        client = AsyncClient(api_key="awsys_test", base_url="https://staging.awsys.co")
        url = client.qr.get_url("test")
        assert "staging.awsys.co" in url

    def test_is_async_context_manager(self):
        """AsyncClient exposes __aenter__ and __aexit__."""
        client = AsyncClient(api_key="awsys_test")
        assert hasattr(client, "__aenter__")
        assert hasattr(client, "__aexit__")
        assert hasattr(client, "aclose")
