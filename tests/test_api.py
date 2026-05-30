from datetime import datetime

from tencent_finance._api import kline_url, quote_url
from tencent_finance.enums import Period, Adjust


class TestKlineUrl:
    def test_a_share_daily(self):
        url = kline_url("sh600000", Period.DAILY, datetime(2024, 1, 1), datetime(2024, 12, 31), Adjust.QFQ)
        assert "proxy.finance.qq.com" in url
        assert "sh600000" in url
        assert "day" in url

    def test_a_share_weekly(self):
        url = kline_url("sz000001", Period.WEEKLY, datetime(2024, 1, 1), datetime(2024, 12, 31), Adjust.HFQ)
        assert "proxy.finance.qq.com" in url
        assert "week" in url

    def test_a_share_minute(self):
        url = kline_url("sh600000", Period.MIN_5, datetime(2024, 1, 1), datetime(2024, 1, 2), Adjust.QFQ)
        assert "ifzq.gtimg.cn" in url
        assert "m5" in url

    def test_hk_daily(self):
        url = kline_url("hk00700", Period.DAILY, datetime(2024, 1, 1), datetime(2024, 12, 31), Adjust.QFQ)
        assert "hkfqkline" in url
        assert "hk00700" in url

    def test_no_adjust(self):
        url = kline_url("sh600000", Period.DAILY, datetime(2024, 1, 1), datetime(2024, 12, 31), Adjust.NONE)
        assert "day" in url


class TestQuoteUrl:
    def test_single_code(self):
        url = quote_url(["sh600000"], 1234567890)
        assert "sqt.gtimg.cn" in url
        assert "sh600000" in url

    def test_multiple_codes(self):
        url = quote_url(["sh600000", "sz000001"], 1234567890)
        assert "sh600000" in url
        assert "sz000001" in url
