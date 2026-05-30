from tencent_finance._http import SyncHttpClient, AsyncHttpClient, RetryConfig, PoolConfig


class TestSyncHttpClient:
    def test_default_config(self):
        c = SyncHttpClient()
        assert c._timeout == (2, 5)

    def test_custom_config(self):
        c = SyncHttpClient(
            retry=RetryConfig(total=5, backoff_factor=1.0),
            pool=PoolConfig(pool_connections=5, pool_maxsize=10),
            timeout=(5, 30),
        )
        assert c._timeout == (5, 30)


class TestRetryConfig:
    def test_defaults(self):
        r = RetryConfig()
        assert r.total == 3
        assert r.backoff_factor == 0.3
        assert r.status_forcelist == (500, 502, 503, 504)

    def test_custom(self):
        r = RetryConfig(total=1, backoff_factor=0.5, status_forcelist=(500,))
        assert r.total == 1
        assert r.status_forcelist == (500,)
