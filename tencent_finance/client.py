from datetime import datetime
from typing import Union, List

import pandas as pd

from .enums import Period, Adjust
from .exceptions import TencentFinanceError
from ._http import SyncHttpClient, AsyncHttpClient, RetryConfig, PoolConfig
from . import kline as _kline
from . import quote as _quote


def _error_df(exc: Exception) -> pd.DataFrame:
    df = pd.DataFrame()
    df.attrs["error"] = True
    df.attrs["error_type"] = type(exc).__name__
    df.attrs["error_message"] = str(exc)
    return df


class Client:
    """Synchronous Tencent finance client."""

    def __init__(
        self,
        retry: RetryConfig | None = None,
        pool: PoolConfig | None = None,
        timeout: tuple[float, float] = (2, 5),
        raise_on_error: bool = True,
    ):
        self._http = SyncHttpClient(retry=retry, pool=pool, timeout=timeout)
        self._raise = raise_on_error

    def get_kline(
        self,
        code: str,
        period: Period,
        start: datetime,
        end: datetime,
        adjust: Adjust = Adjust.QFQ,
    ) -> pd.DataFrame:
        try:
            return _kline.get_kline(self._http, code, period, start, end, adjust)
        except TencentFinanceError as e:
            if self._raise:
                raise
            return _error_df(e)

    def get_quote(
        self,
        stock_codes: Union[str, List[str]],
    ) -> pd.DataFrame:
        try:
            return _quote.get_quote(self._http, stock_codes)
        except TencentFinanceError as e:
            if self._raise:
                raise
            return _error_df(e)


class AsyncClient:
    """Asynchronous Tencent finance client."""

    def __init__(
        self,
        retry: RetryConfig | None = None,
        timeout: tuple[float, float] = (2, 5),
        raise_on_error: bool = True,
    ):
        self._http = AsyncHttpClient(retry=retry, timeout=timeout)
        self._raise = raise_on_error

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._http.close()

    async def get_kline(
        self,
        code: str,
        period: Period,
        start: datetime,
        end: datetime,
        adjust: Adjust = Adjust.QFQ,
    ) -> pd.DataFrame:
        try:
            return await _kline.async_get_kline(self._http, code, period, start, end, adjust)
        except TencentFinanceError as e:
            if self._raise:
                raise
            return _error_df(e)

    async def get_quote(
        self,
        stock_codes: Union[str, List[str]],
    ) -> pd.DataFrame:
        try:
            return await _quote.async_get_quote(self._http, stock_codes)
        except TencentFinanceError as e:
            if self._raise:
                raise
            return _error_df(e)
