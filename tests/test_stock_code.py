import pytest
from tencent_finance._stock_code import detect_market, prefix_code, validate_code
from tencent_finance.exceptions import InvalidCodeError


class TestValidateCode:
    def test_non_string_raises(self):
        with pytest.raises(InvalidCodeError):
            validate_code(123)

    def test_empty_raises(self):
        with pytest.raises(InvalidCodeError):
            validate_code("")

    def test_valid_code_passes(self):
        validate_code("600000")  # should not raise


class TestDetectMarket:
    def test_shanghai_two_digit_prefix(self):
        assert detect_market("600000") == "sh"
        assert detect_market("500000") == "sh"
        assert detect_market("510000") == "sh"
        assert detect_market("900000") == "sh"
        assert detect_market("110000") == "sh"
        assert detect_market("113000") == "sh"
        assert detect_market("132000") == "sh"
        assert detect_market("204000") == "sh"

    def test_shanghai_single_digit_prefix(self):
        assert detect_market("500000") == "sh"
        assert detect_market("600000") == "sh"
        assert detect_market("900000") == "sh"
        assert detect_market("700000") == "sh"

    def test_shenzhen(self):
        assert detect_market("000001") == "sz"
        assert detect_market("300001") == "sz"
        assert detect_market("130001") == "sz"
        assert detect_market("200001") == "sz"

    def test_hong_kong_five_digits(self):
        assert detect_market("00700") == "hk"
        assert detect_market("99888") == "hk"

    def test_already_prefixed(self):
        assert detect_market("sh600000") == "sh"
        assert detect_market("sz000001") == "sz"
        assert detect_market("zz000001") == "zz"
        assert detect_market("usKLAC.OQ") == "us"

    def test_us_bare_ticker(self):
        assert detect_market("KLAC") == "us"
        assert detect_market("AAPL") == "us"
        assert detect_market("JPM") == "us"
        assert detect_market("A") == "us"
        assert detect_market("GOOGL") == "us"


class TestPrefixCode:
    def test_bare_shanghai(self):
        assert prefix_code("600000") == "sh600000"

    def test_bare_shenzhen(self):
        assert prefix_code("000001") == "sz000001"

    def test_bare_hong_kong(self):
        assert prefix_code("00700") == "hk00700"

    def test_already_prefixed(self):
        assert prefix_code("sh600000") == "sh600000"
        assert prefix_code("sz000001") == "sz000001"
        assert prefix_code("hk00700") == "hk00700"
        assert prefix_code("usKLAC.OQ") == "usKLAC.OQ"

    def test_us_bare_ticker(self):
        assert prefix_code("KLAC") == "usKLAC.OQ"
        assert prefix_code("AAPL") == "usAAPL.OQ"
        assert prefix_code("JPM") == "usJPM.OQ"

    def test_empty_raises(self):
        with pytest.raises(InvalidCodeError):
            prefix_code("")
