class TencentFinanceError(Exception):
    """Base exception for all tencent-finance errors."""


class InvalidCodeError(TencentFinanceError):
    """Raised when a stock code is invalid or empty."""


class APIError(TencentFinanceError):
    """Raised when the Tencent API returns an unexpected response."""


class NetworkError(TencentFinanceError):
    """Raised when a network request fails after retries."""
