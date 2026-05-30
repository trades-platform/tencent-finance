"""Integration tests for quote API with real data."""
import pytest

from tencent_finance import Client, AsyncClient


class TestQuoteSync:
    def test_single_stock(self, client: Client):
        df = client.get_quote("600000")
        assert not df.empty
        assert list(df.columns) == ["code", "name", "close", "ratio"]
        assert df.iloc[0]["code"] == "600000"
        assert df.iloc[0]["name"]

    def test_batch_stocks(self, client: Client):
        df = client.get_quote(["600000", "000001"])
        assert len(df) >= 2
        codes = set(df["code"].tolist())
        assert "600000" in codes
        assert "000001" in codes

    def test_hk_stock(self, client: Client):
        df = client.get_quote("00700")
        assert not df.empty

    def test_mixed_markets(self, client: Client):
        df = client.get_quote(["600000", "00700"])
        assert len(df) >= 2


class TestQuoteAsync:
    async def test_single_stock(self, async_client: AsyncClient):
        df = await async_client.get_quote("600000")
        assert not df.empty
        assert list(df.columns) == ["code", "name", "close", "ratio"]

    async def test_batch_stocks(self, async_client: AsyncClient):
        df = await async_client.get_quote(["600000", "000001"])
        assert len(df) >= 2
