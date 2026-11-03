"""Pure domain calculations for sales, marketing, and customer CRM (specs/011-analytics)."""

from dataclasses import dataclass
from datetime import date


def percentage_change(current: int, previous: int) -> float | None:
    """Calculates percentage delta vs previous period; None if previous is 0 and current is 0."""
    if previous <= 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100.0, 1)


def classify_customer_segment(
    *,
    orders_count: int,
    ltv_kopecks: int,
    days_since_last_order: int,
) -> str:
    """Classifies a customer into a marketing CRM segment:
    - vip: 3+ orders or LTV >= 4000 UAH (400_000 kopecks)
    - sleeping: last order > 330 days ago
    - repeat: 2 orders
    - new: 1 order within the last 330 days
    """
    if orders_count >= 3 or ltv_kopecks >= 400_000:
        return "vip"
    if days_since_last_order > 330:
        return "sleeping"
    if orders_count >= 2:
        return "repeat"
    return "new"


@dataclass(frozen=True, slots=True)
class AnniversaryWindow:
    days_until: int
    anniversary_date: date
    years_ago: int


def check_anniversary_window(
    order_date: date,
    *,
    today: date,
    days_before: int = 3,
    days_ahead: int = 14,
) -> AnniversaryWindow | None:
    """Checks if a past-year order has its anniversary within the window."""
    if order_date.year >= today.year:
        return None

    for candidate_year in (today.year, today.year + 1):
        try:
            anniv = order_date.replace(year=candidate_year)
        except ValueError:
            # Feb 29 -> Feb 28 in non-leap years
            anniv = date(candidate_year, 2, 28)

        delta_days = (anniv - today).days
        if -days_before <= delta_days <= days_ahead:
            return AnniversaryWindow(
                days_until=delta_days,
                anniversary_date=anniv,
                years_ago=candidate_year - order_date.year,
            )
    return None
