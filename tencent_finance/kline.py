import json
from datetime import datetime
from typing import Union

import pandas as pd

from .enums import Period, Adjust
from .exceptions import APIError, NetworkError
from ._stock_code import prefix_code
from ._api import kline_url
from ._http import SyncHttpClient, AsyncHttpClient


_KLINE_COLUMNS = ["open", "high", "low", "close", "volume"]


def _parse_kline_response(content: bytes, prefixed_code: str, period: Period, adjust: Adjust) -> pd.DataFrame:
    """Parse A-share kline JSON response into DataFrame."""
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise APIError(f"Failed to parse kline response: {e}") from e

    try:
        stock_data = data["data"][prefixed_code]
    except (KeyError, TypeError) as e:
        raise APIError(f"Unexpected kline response structure: {e}") from e

    # Determine which key holds the kline array
    adjust_val = adjust.value
    unit_map = {"daily": "day", "weekly": "week", "monthly": "month"}
    if period.value in unit_map:
        unit = unit_map[period.value]
    else:
        unit = f"m{period.value}"

    kline_key = f"{adjust_val}{unit}" if adjust_val else unit
    buf = stock_data.get(kline_key) or stock_data.get(unit)
    if buf is None:
        raise APIError(f"Kline data not found for key '{kline_key}' or '{unit}'")

    buf = [row[:6] for row in buf]
    df = pd.DataFrame(buf, columns=["datetime", "open", "close", "high", "low", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df[_KLINE_COLUMNS] = df[_KLINE_COLUMNS].astype(float)
    df = df[["datetime"] + _KLINE_COLUMNS]
    df = df.set_index("datetime")

    # metadata
    try:
        df.attrs["code"] = prefixed_code
        df.attrs["name"] = stock_data["qt"][prefixed_code][1]
        df.attrs["period"] = period.value
    except (KeyError, IndexError):
        df.attrs["code"] = prefixed_code
        df.attrs["name"] = ""
        df.attrs["period"] = period.value

    return df


def _parse_hk_kline_response(content: bytes, prefixed_code: str, period: Period, adjust: Adjust) -> pd.DataFrame:
    """Parse HK market kline response (JS var assignment format)."""
    # HK response starts with JS var assignment like: kline_dayqfq={...}
    first = content.find(b"{")
    if first == -1:
        raise APIError("HK kline response contains no JSON object")

    try:
        data = json.loads(content[first:])
    except json.JSONDecodeError as e:
        raise APIError(f"Failed to parse HK kline response: {e}") from e

    try:
        stock_data = data["data"][prefixed_code]
    except (KeyError, TypeError) as e:
        raise APIError(f"Unexpected HK kline response structure: {e}") from e

    unit_map = {"daily": "day", "weekly": "week", "monthly": "month"}
    unit = unit_map.get(period.value, period.value)

    adjust_val = adjust.value
    kline_key = f"{adjust_val}{unit}" if adjust_val else unit
    buf = stock_data.get(kline_key) or stock_data.get(unit)
    if buf is None:
        raise APIError(f"HK kline data not found for key '{kline_key}' or '{unit}'")

    buf = [row[:6] for row in buf]
    df = pd.DataFrame(buf, columns=["datetime", "open", "close", "high", "low", "volume"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df[_KLINE_COLUMNS] = df[_KLINE_COLUMNS].astype(float)
    df = df[["datetime"] + _KLINE_COLUMNS]
    df = df.set_index("datetime")

    try:
        df.attrs["code"] = prefixed_code
        df.attrs["name"] = stock_data["qt"][prefixed_code][1]
        df.attrs["period"] = period.value
    except (KeyError, IndexError):
        df.attrs["code"] = prefixed_code
        df.attrs["name"] = ""
        df.attrs["period"] = period.value

    return df


def get_kline(
    client: SyncHttpClient,
    code: str,
    period: Period,
    start: datetime,
    end: datetime,
    adjust: Adjust = Adjust.QFQ,
) -> pd.DataFrame:
    """Fetch K-line data synchronously."""
    prefixed = prefix_code(code)
    url = kline_url(prefixed, period, start, end, adjust)

    try:
        resp = client.get(url)
    except Exception as e:
        raise NetworkError(f"K-line request failed: {e}") from e

    if prefixed.startswith("hk"):
        df = _parse_hk_kline_response(resp.content, prefixed, period, adjust)
    else:
        df = _parse_kline_response(resp.content, prefixed, period, adjust)
    df.attrs["code"] = code
    return df


async def async_get_kline(
    client: AsyncHttpClient,
    code: str,
    period: Period,
    start: datetime,
    end: datetime,
    adjust: Adjust = Adjust.QFQ,
) -> pd.DataFrame:
    """Fetch K-line data asynchronously."""
    prefixed = prefix_code(code)
    url = kline_url(prefixed, period, start, end, adjust)

    try:
        resp = await client.get(url)
    except Exception as e:
        raise NetworkError(f"K-line request failed: {e}") from e

    if prefixed.startswith("hk"):
        df = _parse_hk_kline_response(resp.content, prefixed, period, adjust)
    else:
        df = _parse_kline_response(resp.content, prefixed, period, adjust)
    df.attrs["code"] = code
    return df
