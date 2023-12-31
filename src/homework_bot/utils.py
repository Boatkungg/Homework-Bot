import calendar
from datetime import datetime
from typing import List, Union

calendar.setfirstweekday(calendar.SUNDAY)

def check_valid_dates(dates: List[Union[str, None]]):
    valids = []
    for date in dates:
        if date is None:
            valids.append(True)
            continue

        try:
            datetime.strptime(date, "%Y-%m-%d")
            valids.append(True)
        except ValueError:
            valids.append(False)

    return all(valids)


def pretty_time(seconds):
    if seconds >= 1:
        return f"{seconds:.2f}s"

    if seconds >= 0.001:
        return f"{str(round(seconds * 1000)).zfill(3)}ms"

    return f"{str(round(seconds * 1000000)).zfill(3)}µs"


def calendar_label(year, month):
    number_calendar = calendar.monthcalendar(year, month)

    text_calendar = []
    for week in number_calendar:
        text_calendar.append([str(day) if day != 0 else "" for day in week])

    return text_calendar
