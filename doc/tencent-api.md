# Tencent Finance API Protocol

## 1. Real-time Quote

**Endpoint:** `https://sqt.gtimg.cn/?q={codes}&fmt=json&app=wzq&t={timestamp}`

**Parameters:**
- `codes`: comma-separated prefixed codes (e.g. `sh600000,sz000001,hk00700`)
- `fmt`: response format, use `json`
- `app`: fixed `wzq`
- `t`: timestamp in milliseconds

**Response:** JSON object, keyed by prefixed code. Each value is an array:

| Index | Field | Description |
|-------|-------|-------------|
| 1 | name | Stock name |
| 3 | close | Current price |
| 32 | ratio | Price change percentage (涨跌幅) |

**Example:**
```
GET https://sqt.gtimg.cn/?q=sh600000&fmt=json&app=wzq&t=1685000000000

{
  "sh600000": ["1", "浦发银行", "600000", "9.37", "9.21", "9.18", ...]
}
```

---

## 2. K-line (A-share Daily/Weekly/Monthly)

**Endpoint:** `https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get`

**Parameters:**
```
param={prefixed_code},{unit},,,{count},{adjust}
```

- `prefixed_code`: e.g. `sh600000`, `sz000001`
- `unit`: `day` | `week` | `month`
- `count`: number of bars to return
- `adjust`: `qfq` (forward) | `hfq` (backward) | `` (none)

**Note:** The empty field between `unit` and `count` is required (end_date, currently unused).

**Response:**
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "sh600000": {
      "qfqday": [
        ["2026-04-15", "10.05", "10.11", "10.13", "10.03", "430002.00", {}, "0.13", "43393.20", ""],
        ...
      ],
      "qt": { "sh600000": ["1", "浦发银行", ...] }
    }
  }
}
```

K-line array fields (first 6):

| Index | Field |
|-------|-------|
| 0 | datetime (YYYY-MM-DD) |
| 1 | open |
| 2 | close |
| 3 | high |
| 4 | low |
| 5 | volume |

K-line key: `{adjust}{unit}` (e.g. `qfqday`, `hfqweek`, `day`)

---

## 3. K-line (Minute)

**Endpoint:** `https://ifzq.gtimg.cn/appstock/app/kline/mkline`

**Parameters:**
```
param={prefixed_code},{unit},,,{count},{adjust}
```

- `unit`: `m1` | `m5` | `m15` | `m30` | `m60` | `m120`

**Response:** Same structure as daily, but datetime format is `YYYYMMDDHHmm`.

K-line key: `{unit}` (e.g. `m5`) — minute klines do not use adjust prefix.

---

## 4. K-line (HK Market)

**Endpoint:** `https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get`

**Parameters:**
```
_var=kline_{unit}{hk_adjust}&param=hk{code},{unit},,,{count},{hk_adjust}
```

- `hk_adjust`: `qfq` only (HK only supports forward adjust), or empty
- Response wraps in JS variable assignment: `kline_dayqfq={...}`

**Response:** Same structure as A-share daily, but with 10-element arrays including dividend info at index 6.

---

## Stock Code Prefix Rules

| Market | Prefix | Rules |
|--------|--------|-------|
| Shanghai | `sh` | Starts with `50`, `51`, `60`, `90`, `110`, `113`, `132`, `204`, `5`, `6`, `9`, `7` |
| Shenzhen | `sz` | All other codes not matching Shanghai, HK, or US |
| Hong Kong | `hk` | Exactly 5 digits |
| US | `us` | All uppercase letters, 1-5 chars (e.g. `KLAC`, `AAPL`, `GOOGL`) |
| Already prefixed | — | Starts with `sh`, `sz`, `zz`, `us` — use as-is |

---

## 5. US Stock K-line

**Endpoint:** Same as A-share daily (`proxy.finance.qq.com`), with `us` prefix.

**Code format:** `us{TICKER}.OQ` — `.OQ` is a universal suffix for all US stocks.

**Examples:**
```
KLAC    → usKLAC.OQ
AAPL    → usAAPL.OQ
JPM     → usJPM.OQ
GOOGL   → usGOOGL.OQ
```

**Request:**
```
GET https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get?param=usKLAC.OQ,day,,,10,qfq
```

**Response:** Same structure as A-share daily.

**Limitations:**
- Minute kline NOT supported (use daily/weekly/monthly only)
- Real-time quote NOT supported
