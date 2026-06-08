from datetime import date, timedelta
from typing import Iterable


def _easter(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def feriados_br(year: int) -> list[date]:
    p = _easter(year)
    return [
        date(year, 1, 1),
        p - timedelta(48),
        p - timedelta(47),
        p - timedelta(2),
        date(year, 4, 21),
        date(year, 5, 1),
        p + timedelta(60),
        date(year, 9, 7),
        date(year, 10, 12),
        date(year, 11, 2),
        date(year, 11, 15),
        date(year, 11, 20),
        date(year, 12, 25),
    ]


def is_business_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    return d not in feriados_br(d.year)


def business_days(dates: Iterable[date]) -> list[date]:
    return sorted({d for d in dates if is_business_day(d)})
