from dataclasses import dataclass
from typing import Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import httpx

_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"
)


@dataclass
class RetryConfig:
    total: int = 3
    backoff_factor: float = 0.3
    status_forcelist: Tuple[int, ...] = (500, 502, 503, 504)


@dataclass
class PoolConfig:
    pool_connections: int = 10
    pool_maxsize: int = 20


class SyncHttpClient:
    def __init__(
        self,
        retry: RetryConfig | None = None,
        pool: PoolConfig | None = None,
        timeout: Tuple[float, float] = (2, 5),
    ):
        retry = retry or RetryConfig()
        pool = pool or PoolConfig()

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": _USER_AGENT})
        self._timeout = timeout

        adapter = HTTPAdapter(
            pool_connections=pool.pool_connections,
            pool_maxsize=pool.pool_maxsize,
            max_retries=Retry(
                total=retry.total,
                backoff_factor=retry.backoff_factor,
                status_forcelist=retry.status_forcelist,
            ),
        )
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def get(self, url: str) -> requests.Response:
        return self._session.get(url, timeout=self._timeout)


class AsyncHttpClient:
    def __init__(
        self,
        retry: RetryConfig | None = None,
        timeout: Tuple[float, float] = (2, 5),
    ):
        retry = retry or RetryConfig()
        self._client = httpx.AsyncClient(
            headers={"User-Agent": _USER_AGENT},
            timeout=httpx.Timeout(timeout=timeout[1], connect=timeout[0]),
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
        self._retry = retry

    async def get(self, url: str) -> httpx.Response:
        last_exc = None
        for attempt in range(self._retry.total + 1):
            try:
                resp = await self._client.get(url)
                if resp.status_code in self._retry.status_forcelist:
                    if attempt < self._retry.total:
                        import asyncio
                        await asyncio.sleep(self._retry.backoff_factor * (2 ** attempt))
                        continue
                return resp
            except httpx.HTTPError as e:
                last_exc = e
                if attempt < self._retry.total:
                    import asyncio
                    await asyncio.sleep(self._retry.backoff_factor * (2 ** attempt))
                    continue
                raise
        raise last_exc  # type: ignore[misc]

    async def close(self) -> None:
        await self._client.aclose()
