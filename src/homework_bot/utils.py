import calendar
from datetime import datetime
from typing import List, Union


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
    flat_calendar = sum(calendar.monthcalendar(year, month), [])
    flat_calendar[0:0] = [0]  # insert 0 at the beginning of the list
    flat_calendar.extend([0] * (7 - (len(flat_calendar) % 7)))  # pad the end of the list with 0s
    flat_calendar = [
        str(i) if i != 0 else "" for i in flat_calendar
    ]  # convert to strings and replace 0s with empty strings

    reshaped_calendar = [
        flat_calendar[(i * 7) : (7 * (i + 1))] for i in range(len(flat_calendar) // 7)
    ]
    if str().join(reshaped_calendar[0]) == "":
        del reshaped_calendar[0]

    if str().join(reshaped_calendar[-1]) == "":
        del reshaped_calendar[-1]

    return reshaped_calendar
