"""Integration tests for the Me resource."""

from awsysco import Client
from awsysco.models import MeResponse


class TestMe:
    def test_get_returns_me_response(self, client: Client) -> None:
        me = client.me.get()
        assert isinstance(me, MeResponse)

    def test_get_has_email(self, client: Client) -> None:
        me = client.me.get()
        assert me.email is not None
        assert "@" in me.email

    def test_get_has_subscription_tier(self, client: Client) -> None:
        me = client.me.get()
        assert me.subscription_tier is not None
        assert isinstance(me.subscription_tier, str)
