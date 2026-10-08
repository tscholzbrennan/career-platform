from datetime import date, datetime

_DATE_FORMATS = ("%b %Y", "%B %Y", "%Y-%m", "%Y")


def parse_month(value):
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime((value or "").strip(), fmt)
        except ValueError:
            continue
    return None


def duration_months(start, end, today=None):
    """Months covered by a role, counting both the first and last month."""
    began = parse_month(start)
    if began is None:
        return None
    if end:
        ended = parse_month(end)
        if ended is None:
            return None
    else:
        ended = today or date.today()
    return (ended.year - began.year) * 12 + ended.month - began.month + 1


def total_months(experiences):
    durations = [duration_months(item.start_date, item.end_date) for item in experiences]
    return sum(months for months in durations if months is not None)
