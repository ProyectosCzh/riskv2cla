"""
SmartRisk - Display Formatters
"""


def fmt_currency(value: float, decimals: int = 0) -> str:
    return f"${value:,.{decimals}f}"


def fmt_percent(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}%}"


def fmt_number(value: float, decimals: int = 2) -> str:
    return f"{value:,.{decimals}f}"


def fmt_ratio(value: float) -> str:
    return f"{value:.3f}"


def risk_color(value: float, low: float = 0.0, high: float = 1.0, invert: bool = False) -> str:
    """Return a hex color between green and red based on normalized value."""
    norm = max(0.0, min(1.0, (value - low) / (high - low + 1e-10)))
    if invert:
        norm = 1 - norm
    # Green → Yellow → Red
    if norm < 0.5:
        r = int(norm * 2 * 221)
        g = 161
    else:
        r = 221
        g = int((1 - norm) * 2 * 161)
    return f"rgb({r},{g},46)"
