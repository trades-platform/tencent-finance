# tencent-finance

Tencent stock market data library with sync and async support.

## Install

```bash
pip install -e .
```

## Quick Start

```python
from datetime import datetime, timedelta
from tencent_finance import Client, AsyncClient, Period, Adjust

# Sync
client = Client()
end = datetime.now()
start = end - timedelta(days=30)

df = client.get_kline("600000", Period.DAILY, start, end, Adjust.QFQ)
print(df.head())
#              open   high    low  close    volume
# datetime
# 2026-04-15  10.05  10.13  10.03  10.11  430002.0

df = client.get_quote(["600000", "000001"])
print(df)
#      code  name  close  ratio
# 0  600000  浦发银行   9.37   1.74
# 1  000001  平安银行  11.25   0.45

# Async
async with AsyncClient() as client:
    df = await client.get_kline("00700", Period.DAILY, start, end)
    df = await client.get_quote(["600000", "00700"])
```

## Error Handling

```python
# Default: raise exceptions
from tencent_finance.exceptions import TencentFinanceError, InvalidCodeError, APIError, NetworkError

try:
    df = client.get_kline("bad_code", Period.DAILY, start, end)
except InvalidCodeError:
    print("invalid code")

# Silent mode: return empty DataFrame, error in df.attrs
client = Client(raise_on_error=False)
df = client.get_kline("bad_code", Period.DAILY, start, end)
if df.attrs.get("error"):
    print(df.attrs["error_type"], df.attrs["error_message"])
```

## Configuration

```python
from tencent_finance._http import RetryConfig, PoolConfig

client = Client(
    retry=RetryConfig(total=5, backoff_factor=1.0),
    pool=PoolConfig(pool_connections=20, pool_maxsize=50),
    timeout=(5, 30),
    raise_on_error=False,
)
```
