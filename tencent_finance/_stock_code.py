from .exceptions import InvalidCodeError

_SHANGHAI_PREFIXES = ("50", "51", "60", "90", "110", "113", "132", "204")
_SHANGHAI_SINGLE = ("5", "6", "9", "7")


def validate_code(code: str) -> None:
    """Raise InvalidCodeError if code is not a valid stock code."""
    if not isinstance(code, str):
        raise InvalidCodeError(f"Stock code must be a string, got {type(code).__name__}")
    if not code:
        raise InvalidCodeError("Stock code must not be empty")


def detect_market(code: str) -> str:
    """Detect market (sh, sz, hk, us) from a stock code.

    Returns the market prefix string. For already-prefixed codes (e.g. "sh600000"),
    returns the prefix as-is.
    """
    validate_code(code)

    if code.startswith(("sh", "sz", "zz", "us")):
        return code[:2]

    # HK: exactly 5 digits
    if len(code) == 5 and code.isdigit():
        return "hk"

    # Shanghai: 2-char prefixes or 1-char prefixes
    if code.startswith(_SHANGHAI_PREFIXES) or code.startswith(_SHANGHAI_SINGLE):
        return "sh"

    # US: all uppercase letters, 1-5 chars
    if code.isalpha() and code.isupper() and 1 <= len(code) <= 5:
        return "us"

    return "sz"


def prefix_code(code: str) -> str:
    """Convert bare stock code to prefixed form for API calls.

    Examples: "600000" -> "sh600000", "000001" -> "sz000001", "00700" -> "hk00700",
    "KLAC" -> "usKLAC.OQ"
    Already-prefixed codes are returned as-is.
    """
    validate_code(code)

    if code.startswith(("sh", "sz", "hk", "zz", "us")):
        return code

    market = detect_market(code)
    if market == "us":
        return f"us{code}.OQ"
    return f"{market}{code}"
