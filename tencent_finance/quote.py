import json
import time
from typing import Union, List

import pandas as pd

from .exceptions import APIError, NetworkError
from ._stock_code import prefix_code, validate_code
from ._api import quote_url
from ._http import SyncHttpClient, AsyncHttpClient


_QUOTE_COLUMNS = ["code", "name", "close", "ratio"]


def _parse_quote_response(text: str, codes: list[str], prefixed_codes: list[str]) -> pd.DataFrame:
    """Parse quote JSON response into DataFrame."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise APIError(f"Failed to parse quote response: {e}") from e

    results = []
    for i, prefixed in enumerate(prefixed_codes):
        if prefixed in data and isinstance(data[prefixed], list):
            arr = data[prefixed]
            original_code = codes[i]
            name = arr[1] if len(arr) > 1 else ""
            close = float(arr[3]) if len(arr) > 3 and arr[3] else 0.0
            ratio = float(arr[32]) if len(arr) > 32 and arr[32] else 0.0
            results.append({
                "code": original_code,
                "name": name,
                "close": close,
                "ratio": ratio,
            })

    if not results:
        raise APIError("No valid quote data found in response")

    return pd.DataFrame(results, columns=_QUOTE_COLUMNS)


def get_quote(
    client: SyncHttpClient,
    stock_codes: Union[str, List[str]],
) -> pd.DataFrame:
    """Fetch real-time quote data synchronously."""
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    for code in stock_codes:
        validate_code(code)

    codes = list(stock_codes)
    prefixed_codes = [prefix_code(c) for c in codes]
    timestamp = int(time.time() * 1000)
    url = quote_url(prefixed_codes, timestamp)

    try:
        resp = client.get(url)
    except Exception as e:
        raise NetworkError(f"Quote request failed: {e}") from e

    return _parse_quote_response(resp.text, codes, prefixed_codes)


async def async_get_quote(
    client: AsyncHttpClient,
    stock_codes: Union[str, List[str]],
) -> pd.DataFrame:
    """Fetch real-time quote data asynchronously."""
    if isinstance(stock_codes, str):
        stock_codes = [stock_codes]

    for code in stock_codes:
        validate_code(code)

    codes = list(stock_codes)
    prefixed_codes = [prefix_code(c) for c in codes]
    timestamp = int(time.time() * 1000)
    url = quote_url(prefixed_codes, timestamp)

    try:
        resp = await client.get(url)
    except Exception as e:
        raise NetworkError(f"Quote request failed: {e}") from e

    return _parse_quote_response(resp.text, codes, prefixed_codes)
