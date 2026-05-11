from __future__ import annotations

import calendar
import re
from datetime import date, timedelta

WEEKDAYS: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}

MONTHS: dict[str, int] = {
    "january": 1, "jan": 1, "february": 2, "feb": 2,
    "march": 3, "mar": 3, "april": 4, "apr": 4, "may": 5,
    "june": 6, "jun": 6, "july": 7, "jul": 7,
    "august": 8, "aug": 8, "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10, "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}

NUMBER_WORDS: dict[str, int] = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "eleven": 11, "twelve": 12, "a": 1, "an": 1,
}


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()
    text = _normalize(s)
    result = _parse(text, today)
    if result is None:
        raise ValueError(f"Could not parse date: {s!r}")
    return result


def _normalize(s: str) -> str:
    text = s.strip().lower()
    text = re.sub(r"(\d+)(st|nd|rd|th)\b", r"\1", text)  # 1st -> 1
    text = text.replace(",", " ")
    return re.sub(r"\s+", " ", text).strip()


def _parse(text: str, today: date) -> date | None:
    if text in ("today", "now"):
        return today
    if text == "tomorrow":
        return today + timedelta(days=1)
    if text == "yesterday":
        return today - timedelta(days=1)

    # ISO: 2025-12-01
    m = re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
    if m:
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))

    # US slash: 12/1/2025  or  12/1/25
    m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{2,4})", text)
    if m:
        month, day, year = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if year < 100:
            year += 2000
        return date(year, month, day)

    # "N <unit>s before/after/from X"
    m = re.fullmatch(
        r"(\w+)\s+(day|week|month|year)s?\s+(before|after|from)\s+(.+)",
        text,
    )
    if m:
        n = _to_int(m.group(1))
        if n is None:
            return None
        unit, direction, rest = m.group(2), m.group(3), m.group(4)
        base = today if rest in ("now", "today") else _parse(rest, today)
        if base is None:
            return None
        sign = -1 if direction == "before" else 1
        return _shift(base, sign * n, unit)

    # "in N <unit>s"
    m = re.fullmatch(r"in\s+(\w+)\s+(day|week|month|year)s?", text)
    if m:
        n = _to_int(m.group(1))
        if n is None:
            return None
        return _shift(today, n, m.group(2))

    # "N <unit>s ago"
    m = re.fullmatch(r"(\w+)\s+(day|week|month|year)s?\s+ago", text)
    if m:
        n = _to_int(m.group(1))
        if n is None:
            return None
        return _shift(today, -n, m.group(2))

    # "next/last/this <weekday>"
    m = re.fullmatch(r"(next|last|this)\s+(\w+)", text)
    if m and m.group(2) in WEEKDAYS:
        direction = m.group(1)
        target = WEEKDAYS[m.group(2)]
        current = today.weekday()
        if direction == "next":
            diff = (target - current) % 7 or 7
        elif direction == "last":
            diff = (target - current) % 7 - 7
            if diff == 0:
                diff = -7
        else:  # this
            diff = (target - current) % 7
        return today + timedelta(days=diff)

    # "<Month> <day> [<year>]"
    m = re.fullmatch(r"(\w+)\s+(\d{1,2})(?:\s+(\d{2,4}))?", text)
    if m and m.group(1) in MONTHS:
        return _build_date(MONTHS[m.group(1)], int(m.group(2)), m.group(3), today)

    # "<day> <Month> [<year>]"
    m = re.fullmatch(r"(\d{1,2})\s+(\w+)(?:\s+(\d{2,4}))?", text)
    if m and m.group(2) in MONTHS:
        return _build_date(MONTHS[m.group(2)], int(m.group(1)), m.group(3), today)

    return None


def _build_date(month: int, day: int, year_str: str | None, today: date) -> date:
    if year_str:
        year = int(year_str)
        if year < 100:
            year += 2000
    else:
        year = today.year
    return date(year, month, day)


def _to_int(s: str) -> int | None:
    if s.isdigit():
        return int(s)
    return NUMBER_WORDS.get(s)


def _shift(d: date, n: int, unit: str) -> date:
    if unit == "day":
        return d + timedelta(days=n)
    if unit == "week":
        return d + timedelta(weeks=n)
    if unit == "month":
        return _shift_months(d, n)
    if unit == "year":
        return _shift_months(d, 12 * n)
    return d


def _shift_months(d: date, n: int) -> date:
    month_idx = d.month - 1 + n
    year = d.year + month_idx // 12
    month = month_idx % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(d.day, last_day))

