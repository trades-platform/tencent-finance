from datetime import datetime
from typing import Optional

from .enums import Period, Adjust

_KLINE_DAILY_MAP = {"daily": "day", "weekly": "week", "monthly": "month"}


def _kline_count(start: datetime, end: datetime, period: Period) -> int:
    delta = end - start
    if period == Period.DAILY:
        return max(delta.days, 1)
    if period == Period.WEEKLY:
        return max(int(delta.days / 7), 1)
    if period == Period.MONTHLY:
        return max(int(delta.days / 30), 1)
    # minute periods
    min_map = {"1": 240, "5": 48, "15": 16, "30": 8, "60": 4, "120": 2}
    per_day = min_map.get(period.value, 48)
    return max(int(delta.days / 7 * 5 * per_day), 1)


def kline_url(
    prefixed_code: str,
    period: Period,
    start: datetime,
    end: datetime,
    adjust: Adjust,
) -> str:
    count = _kline_count(start, end, period)
    adjust_val = adjust.value

    market = prefixed_code[:2]

    if market == "hk":
        unit = _KLINE_DAILY_MAP.get(period.value, period.value)
        hk_adjust = adjust_val if adjust_val == "qfq" else ""
        return (
            f"https://web.ifzq.gtimg.cn/appstock/app/hkfqkline/get"
            f"?_var=kline_{unit}{hk_adjust}"
            f"&param={prefixed_code},{unit},,,{count},{hk_adjust}"
        )

    # A-share
    if period.value in _KLINE_DAILY_MAP:
        unit = _KLINE_DAILY_MAP[period.value]
        return (
            f"https://proxy.finance.qq.com/ifzqgtimg/appstock/app/newfqkline/get"
            f"?param={prefixed_code},{unit},,,{count},{adjust_val}"
        )

    # minute kline
    unit = f"m{period.value}"
    return (
        f"https://ifzq.gtimg.cn/appstock/app/kline/mkline"
        f"?param={prefixed_code},{unit},,,{count},{adjust_val}"
    )


def quote_url(prefixed_codes: list[str], timestamp: int) -> str:
    codes_str = ",".join(prefixed_codes)
    return f"https://sqt.gtimg.cn/?q={codes_str}&fmt=json&app=wzq&t={timestamp}"
