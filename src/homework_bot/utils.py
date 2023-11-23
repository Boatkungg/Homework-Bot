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
        return f"{seconds * 1000:.2f}ms"

    return f"{seconds * 1000000:.2f}µs"
