"""Integration tests for the Analytics resource."""

import time

from awsysco import Client
from awsysco.models import LinkStats


def _unique_url() -> str:
    return f"https://example.com/sdk-analytics-{int(time.time() * 1000)}"


class TestAnalytics:
    def test_get_stats_returns_link_stats(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        stats = client.analytics.get_stats(short_code)
        assert isinstance(stats, LinkStats)
        assert stats.total_clicks is not None
        assert isinstance(stats.total_clicks, int)

    def test_get_stats_has_clicks_list(self, client: Client) -> None:
        created = client.links.create(_unique_url())
        short_code = created.short_code
        assert short_code is not None

        stats = client.analytics.get_stats(short_code)
        assert isinstance(stats.clicks, list)
