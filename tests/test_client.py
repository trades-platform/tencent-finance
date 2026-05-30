"""End-to-end client tests."""
import pytest
from datetime import datetime, timedelta

from tencent_finance import Client, AsyncClient, Period, Adjust
from tencent_finance.exceptions import InvalidCodeError
from tencent_finance._http import RetryConfig


class TestClientSync:
    def test_invalid_code_raises(self, client: Client):
        with pytest.raises(InvalidCodeError):
            client.get_kline("", Period.DAILY, datetime.now(), datetime.now())

    def test_quote_invalid_code_raises(self, client: Client):
        with pytest.raises(InvalidCodeError):
            client.get_quote("")

    def test_custom_retry_config(self):
        c = Client(retry=RetryConfig(total=1, backoff_factor=0.1))
        end = datetime.now()
        start = end - timedelta(days=5)
        df = c.get_kline("600000", Period.DAILY, start, end)
        assert not df.empty


class TestRaiseOnError:
    def test_kline_returns_empty_df_on_invalid_code(self):
        c = Client(raise_on_error=False)
        df = c.get_kline("", Period.DAILY, datetime.now(), datetime.now())
        assert df.empty
        assert df.attrs["error"] is True
        assert df.attrs["error_type"] == "InvalidCodeError"
        assert df.attrs["error_message"]

    def test_quote_returns_empty_df_on_invalid_code(self):
        c = Client(raise_on_error=False)
        df = c.get_quote("")
        assert df.empty
        assert df.attrs["error"] is True
        assert df.attrs["error_type"] == "InvalidCodeError"

    def test_kline_normal_has_no_error_attr(self, client: Client):
        end = datetime.now()
        start = end - timedelta(days=5)
        df = client.get_kline("600000", Period.DAILY, start, end)
        assert "error" not in df.attrs


class TestClientAsync:
    async def test_invalid_code_raises(self, async_client: AsyncClient):
        with pytest.raises(InvalidCodeError):
            await async_client.get_kline("", Period.DAILY, datetime.now(), datetime.now())
