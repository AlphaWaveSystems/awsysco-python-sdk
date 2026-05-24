"""Unit tests for the QR resource — no HTTP calls made."""

import pytest

from awsysco import Client


class TestQR:
    def test_get_url_returns_string(self, client: Client) -> None:
        url = client.qr.get_url("abc123")
        assert isinstance(url, str)

    def test_get_url_contains_short_code(self, client: Client) -> None:
        url = client.qr.get_url("testcode")
        assert "testcode" in url

    def test_get_url_default_params(self, client: Client) -> None:
        url = client.qr.get_url("abc123")
        assert "size=300" in url
        assert "color=000000" in url
        assert "bgColor=FFFFFF" in url

    def test_get_url_custom_size(self, client: Client) -> None:
        url = client.qr.get_url("abc123", size=400)
        assert "size=400" in url

    def test_get_url_custom_color(self, client: Client) -> None:
        url = client.qr.get_url("abc123", color="FF0000", bg_color="FFFFFF")
        assert "color=FF0000" in url

    def test_get_url_path_structure(self, client: Client) -> None:
        url = client.qr.get_url("mycode")
        assert "/api/qr/mycode" in url
