from enum import Enum


class Period(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MIN_1 = "1"
    MIN_5 = "5"
    MIN_15 = "15"
    MIN_30 = "30"
    MIN_60 = "60"
    MIN_120 = "120"


class Adjust(Enum):
    QFQ = "qfq"
    HFQ = "hfq"
    NONE = ""
