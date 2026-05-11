from datetime import date
from nldate import parse

TODAY = date(2025, 12, 1)  # Monday


def test_today():
    assert parse("today", today=TODAY) == TODAY


def test_tomorrow():
    assert parse("tomorrow", today=TODAY) == date(2025, 12, 2)


def test_yesterday():
    assert parse("yesterday", today=TODAY) == date(2025, 11, 30)


def test_iso():
    assert parse("2025-12-01") == date(2025, 12, 1)


def test_explicit_long():
    assert parse("December 1, 2025") == date(2025, 12, 1)


def test_explicit_ordinal():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_days_before():
    assert parse("5 days before December 1, 2025") == date(2025, 11, 26)


def test_days_after():
    assert parse("3 days after December 1, 2025") == date(2025, 12, 4)


def test_next_weekday():
    assert parse("next Tuesday", today=TODAY) == date(2025, 12, 2)


def test_last_weekday():
    assert parse("last Friday", today=TODAY) == date(2025, 11, 28)
