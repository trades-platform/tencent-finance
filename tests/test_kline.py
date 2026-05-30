"""Integration tests for kline API with real data."""
import pytest
from datetime import datetime, timedelta

from tencent_finance import Client, AsyncClient, Period, Adjust
from tencent_finance.exceptions import APIError


@pytest.fixture
def start():
    return datetime.now() - timedelta(days=30)


@pytest.fixture
def end():
    return datetime.now()


class TestKlineSync:
    def test_a_share_daily(self, client: Client, start, end):
        df = client.get_kline("600000", Period.DAILY, start, end, Adjust.QFQ)
        assert not df.empty
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert df.index.name == "datetime"
        assert df.attrs["code"] == "600000"
        assert df.attrs["name"]
        assert df.attrs["period"] == "daily"

    def test_a_share_minute(self, client: Client, start, end):
        df = client.get_kline("000001", Period.MIN_5, start, end)
        assert not df.empty
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]

    def test_hk_daily(self, client: Client, start, end):
        df = client.get_kline("00700", Period.DAILY, start, end, Adjust.QFQ)
        assert not df.empty
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert df.attrs["period"] == "daily"

    def test_already_prefixed(self, client: Client, start, end):
        df = client.get_kline("sh600000", Period.DAILY, start, end)
        assert not df.empty

    def test_no_adjust(self, client: Client, start, end):
        df = client.get_kline("600000", Period.DAILY, start, end, Adjust.NONE)
        assert not df.empty


class TestKlineUS:
    def test_us_daily_bare_ticker(self, client: Client, start, end):
        df = client.get_kline("KLAC", Period.DAILY, start, end)
        assert not df.empty
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]
        assert df.attrs["code"] == "KLAC"
        assert df.attrs["name"]

    def test_us_daily_aapl(self, client: Client, start, end):
        df = client.get_kline("AAPL", Period.DAILY, start, end)
        assert not df.empty
        assert df.attrs["code"] == "AAPL"

    def test_us_daily_jpm(self, client: Client, start, end):
        df = client.get_kline("JPM", Period.DAILY, start, end)
        assert not df.empty

    def test_us_already_prefixed(self, client: Client, start, end):
        df = client.get_kline("usKLAC.OQ", Period.DAILY, start, end)
        assert not df.empty
        assert df.attrs["code"] == "usKLAC.OQ"

    def test_us_minute_raises(self, client: Client, start, end):
        with pytest.raises(APIError, match="US stock minute kline"):
            client.get_kline("KLAC", Period.MIN_5, start, end)


class TestKlineAsync:
    async def test_a_share_daily(self, async_client: AsyncClient, start, end):
        df = await async_client.get_kline("600000", Period.DAILY, start, end)
        assert not df.empty
        assert list(df.columns) == ["open", "high", "low", "close", "volume"]

    async def test_hk_daily(self, async_client: AsyncClient, start, end):
        df = await async_client.get_kline("00700", Period.DAILY, start, end)
        assert not df.empty
